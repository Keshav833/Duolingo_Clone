"""
Schema for GET /api/skills/{skill_id}/lessons.

Reuses SkillOut from schemas/course.py for the skill portion, since it's
already exactly the shape needed here (id, title, icon, order, status,
crowns, lessons_completed) — no need for a second near-duplicate schema.

LessonSummaryOut intentionally exposes only id, order, and xp_reward.
No exercises, no correct_answer, no completion state yet (not required
by this task).
"""

from typing import List

from pydantic import BaseModel, ConfigDict

from .course import SkillOut


class LessonSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order: int
    xp_reward: int


class SkillLessonsOut(BaseModel):
    skill: SkillOut
    lessons: List[LessonSummaryOut]