from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models import SkillStatus  # VERIFY: this is where your enum lives


class SkillProgressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: SkillStatus
    crowns: int
    lessons_completed: int


class CompleteLessonResponse(BaseModel):
    lesson_completed: bool
    already_completed: bool
    xp_earned: int
    total_xp: int
    daily_xp_earned: int
    streak: int
    skill: SkillProgressOut
    unlocked_skill_id: Optional[int] = None