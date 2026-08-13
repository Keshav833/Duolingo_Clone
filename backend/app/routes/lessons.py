"""
Lesson route — returns a lesson and its exercises for the lesson player.

response_model=LessonOut does the actual work of hiding correct_answer:
since Exercise (the ORM object) has correct_answer but ExerciseOut (the
schema) doesn't declare that field, FastAPI's serialization step drops it
before the JSON ever reaches the client. There's no manual "delete this key"
step needed or forgettable.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas.lesson import LessonOut

router = APIRouter(prefix="/api", tags=["lessons"])


@router.get("/lessons/{lesson_id}", response_model=LessonOut)
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if lesson is None:
        raise HTTPException(status_code=404, detail=f"Lesson {lesson_id} not found.")
    return lesson