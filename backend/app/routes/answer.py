# backend/app/routes/answer.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Union, List, Dict, Any

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Exercise, Lesson, UserStats, User, ExerciseType
from app.schemas.answer import AnswerSubmitRequest, AnswerSubmitResponse

router = APIRouter()


def _norm(s: str) -> str:
    """Case/whitespace-insensitive compare for typed and free-text answers."""
    return s.strip().lower()


def _is_correct(exercise: Exercise, submitted: Union[str, List[str], Dict[str, str]]) -> bool:
    """
    Each exercise type stores correct_answer in its own JSON envelope
    (see models.py comments), so comparison logic branches on type rather
    than doing a single `submitted == exercise.correct_answer`.
    """
    correct = exercise.correct_answer

    if exercise.type in (
        ExerciseType.multiple_choice,
        ExerciseType.type_answer,
        ExerciseType.fill_blank,
    ):
        if not isinstance(submitted, str):
            return False
        expected = correct.get("correct", "")
        return _norm(submitted) == _norm(expected)

    if exercise.type == ExerciseType.translate:
        if not isinstance(submitted, list):
            return False
        expected = correct.get("correct", [])
        if len(submitted) != len(expected):
            return False
        return all(_norm(a) == _norm(b) for a, b in zip(submitted, expected))

    if exercise.type == ExerciseType.match_pairs:
        # match_pairs correct_answer has no "correct" wrapper key —
        # it's a direct {source_word: target_word} mapping per the schema.
        if not isinstance(submitted, dict):
            return False
        if set(submitted.keys()) != set(correct.keys()):
            return False
        return all(_norm(submitted[k]) == _norm(v) for k, v in correct.items())

    return False


def _display_answer(exercise: Exercise) -> Union[str, List[str], Dict[str, str]]:
    """What we hand back to the UI for feedback after submission."""
    if exercise.type == ExerciseType.match_pairs:
        return exercise.correct_answer
    return exercise.correct_answer.get("correct")


@router.post("/api/lessons/{lesson_id}/answer", response_model=AnswerSubmitResponse)
def submit_answer(
    lesson_id: int,
    payload: AnswerSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    exercise = db.query(Exercise).filter(Exercise.id == payload.exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    if exercise.lesson_id != lesson_id:
        raise HTTPException(status_code=400, detail="Exercise does not belong to this lesson")

    stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).first()
    if not stats:
        # Shouldn't happen for the seeded user, but fail loudly instead of
        # silently 500-ing on stats.hearts below.
        raise HTTPException(status_code=404, detail="User stats not found")

    correct = _is_correct(exercise, payload.submitted_answer)

    if not correct:
        stats.hearts = max(0, stats.hearts - 1)
        db.commit()
        db.refresh(stats)

    return AnswerSubmitResponse(
        correct=correct,
        hearts=stats.hearts,
        correct_answer=_display_answer(exercise),
    )