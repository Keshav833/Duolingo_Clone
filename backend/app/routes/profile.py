"""
Profile route — learner stats page.

progress counts are derived from persistent UserSkillProgress /
UserLessonProgress rows (never hardcoded), read off current_user's
already-loaded relationships — same trick course.py uses for skill
progress, so no extra queries.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..dependencies import get_current_user
from ..schemas.profile import ProfileOut, ProfileStatsOut, ProfileProgressOut

router = APIRouter(prefix="/api", tags=["profile"])


@router.get("/profile", response_model=ProfileOut)
def get_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.stats is None:
        # Shouldn't happen post-seed (every user gets a UserStats row),
        # but fail loudly instead of returning a broken response.
        raise HTTPException(status_code=404, detail="User stats not found.")

    skills_completed = sum(
        1 for p in current_user.skill_progress if p.status == models.SkillStatus.completed
    )
    lessons_completed = sum(1 for p in current_user.lesson_progress if p.completed)

    return ProfileOut(
        id=current_user.id,
        username=current_user.username,
        stats=ProfileStatsOut.model_validate(current_user.stats),
        progress=ProfileProgressOut(
            skills_completed=skills_completed,
            lessons_completed=lessons_completed,
        ),
    )