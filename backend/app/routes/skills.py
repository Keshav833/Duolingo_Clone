"""
Skill-lessons route — powers the lesson-selection screen for a single skill.

Same merge pattern as routes/course.py: Skill (static) + UserSkillProgress
(per-user) combined into SkillOut. Lessons are queried directly and ordered
by Lesson.order, same as the relationship ordering defined in models.py.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..dependencies import get_current_user
from ..schemas.course import SkillOut
from ..schemas.skills import SkillLessonsOut, LessonSummaryOut

router = APIRouter(prefix="/api", tags=["skills"])


@router.get("/skills/{skill_id}/lessons", response_model=SkillLessonsOut)
def get_skill_lessons(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found.")

    progress = (
        db.query(models.UserSkillProgress)
        .filter(
            models.UserSkillProgress.user_id == current_user.id,
            models.UserSkillProgress.skill_id == skill_id,
        )
        .first()
    )

    skill_out = SkillOut(
        id=skill.id,
        title=skill.title,
        icon=skill.icon,
        order=skill.order,
        status=progress.status if progress else models.SkillStatus.locked,
        crowns=progress.crowns if progress else 0,
        lessons_completed=progress.lessons_completed if progress else 0,
    )

    lessons = (
        db.query(models.Lesson)
        .filter(models.Lesson.skill_id == skill_id)
        .order_by(models.Lesson.order)
        .all()
    )
    lessons_out = [
        LessonSummaryOut(id=l.id, order=l.order, xp_reward=l.xp_reward) for l in lessons
    ]

    return SkillLessonsOut(skill=skill_out, lessons=lessons_out)