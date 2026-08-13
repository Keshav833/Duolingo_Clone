from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Lesson, Skill, Unit, User, UserLessonProgress, UserSkillProgress, SkillStatus
from app.schemas.complete import CompleteLessonResponse, SkillProgressOut

router = APIRouter(prefix="/api/lessons", tags=["lessons"])


def _get_next_skill(db: Session, current_skill_id: int) -> Skill | None:
    """Skills ordered globally by (unit order, skill order) within the course."""
    ordered_skills = (
        db.query(Skill)
        .join(Unit, Skill.unit_id == Unit.id)
        .order_by(Unit.order, Skill.order)
        .all()
    )
    for i, s in enumerate(ordered_skills):
        if s.id == current_skill_id:
            if i + 1 < len(ordered_skills):
                return ordered_skills[i + 1]
            return None
    return None


def _build_response(
    lesson_completed: bool,
    already_completed: bool,
    xp_earned: int,
    stats,
    skill_progress: UserSkillProgress,
    unlocked_skill_id: int | None,
) -> CompleteLessonResponse:
    return CompleteLessonResponse(
        lesson_completed=lesson_completed,
        already_completed=already_completed,
        xp_earned=xp_earned,
        total_xp=stats.xp_total,
        daily_xp_earned=stats.daily_xp_earned,
        streak=stats.streak_count,
        skill=SkillProgressOut(
            id=skill_progress.skill_id,
            status=skill_progress.status,
            crowns=skill_progress.crowns,
            lessons_completed=skill_progress.lessons_completed,
        ),
        unlocked_skill_id=unlocked_skill_id,
    )


@router.post("/{lesson_id}/complete", response_model=CompleteLessonResponse)
def complete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    stats = current_user.stats

    progress = (
        db.query(UserLessonProgress)
        .filter(
            UserLessonProgress.user_id == current_user.id,
            UserLessonProgress.lesson_id == lesson_id,
        )
        .first()
    )

    skill_progress = (
        db.query(UserSkillProgress)
        .filter(
            UserSkillProgress.user_id == current_user.id,
            UserSkillProgress.skill_id == lesson.skill_id,
        )
        .first()
    )

    # --- Duplicate completion: short-circuit, no side effects ---
    if progress is not None and progress.completed:
        if skill_progress is None:
            # Defensive fallback only — shouldn't happen if data is consistent,
            # since a completed lesson implies skill progress was created.
            skill_progress = UserSkillProgress(
                user_id=current_user.id,
                skill_id=lesson.skill_id,
                status=SkillStatus.available,
                crowns=0,
                lessons_completed=0,
            )
        return _build_response(
            lesson_completed=True,
            already_completed=True,
            xp_earned=0,
            stats=stats,
            skill_progress=skill_progress,
            unlocked_skill_id=None,
        )

    # --- First completion ---
    now = datetime.now(UTC)
    today = now.date()

    if progress is None:
        progress = UserLessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            completed=True,
            xp_earned=lesson.xp_reward,
            completed_at=now,
        )
        db.add(progress)
    else:
        # A row may already exist (e.g. accuracy tracked during /answer) but not yet completed.
        progress.completed = True
        progress.xp_earned = lesson.xp_reward
        progress.completed_at = now

    # XP
    stats.xp_total += lesson.xp_reward
    stats.daily_xp_earned += lesson.xp_reward

    # Streak
    # last_activity_date is a DateTime column, so it must be compared as a date
    # via .date() rather than compared directly against a date object.
    last_activity = (
        stats.last_activity_date.date()
        if stats.last_activity_date is not None
        else None
    )

    if last_activity is None:
        stats.streak_count = 1
    elif last_activity == today:
        pass  # already active today, unchanged
    elif (today - last_activity).days == 1:
        stats.streak_count += 1
    else:
        stats.streak_count = 1

    stats.last_activity_date = now  # store full datetime, not date()

    # Skill progress
    if skill_progress is None:
        skill_progress = UserSkillProgress(
            user_id=current_user.id,
            skill_id=lesson.skill_id,
            status=SkillStatus.available,
            crowns=0,
            lessons_completed=0,
        )
        db.add(skill_progress)

    skill_progress.lessons_completed += 1
    skill_progress.crowns = skill_progress.lessons_completed

    total_lessons_in_skill = (
        db.query(Lesson).filter(Lesson.skill_id == lesson.skill_id).count()
    )

    unlocked_skill_id = None

    if skill_progress.lessons_completed >= total_lessons_in_skill:
        skill_progress.status = SkillStatus.completed

        next_skill = _get_next_skill(db, lesson.skill_id)
        if next_skill is not None:
            next_progress = (
                db.query(UserSkillProgress)
                .filter(
                    UserSkillProgress.user_id == current_user.id,
                    UserSkillProgress.skill_id == next_skill.id,
                )
                .first()
            )
            if next_progress is None:
                next_progress = UserSkillProgress(
                    user_id=current_user.id,
                    skill_id=next_skill.id,
                    status=SkillStatus.available,
                    crowns=0,
                    lessons_completed=0,
                )
                db.add(next_progress)
            elif next_progress.status == SkillStatus.locked:
                next_progress.status = SkillStatus.available
            unlocked_skill_id = next_skill.id

    db.commit()
    db.refresh(stats)
    db.refresh(skill_progress)

    return _build_response(
        lesson_completed=True,
        already_completed=False,
        xp_earned=lesson.xp_reward,
        stats=stats,
        skill_progress=skill_progress,
        unlocked_skill_id=unlocked_skill_id,
    )