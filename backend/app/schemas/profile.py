"""
Schema for GET /api/profile.

progress.skills_completed / progress.lessons_completed are computed in the
route from UserSkillProgress / UserLessonProgress — not stored fields, so
there's no ORM model that maps 1:1 to ProfileOut (same pattern as CourseOut
in schemas/course.py).
"""

from pydantic import BaseModel, ConfigDict


class ProfileStatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    xp_total: int
    streak_count: int
    hearts: int
    hearts_max: int
    daily_xp_goal: int
    daily_xp_earned: int


class ProfileProgressOut(BaseModel):
    skills_completed: int
    lessons_completed: int


class ProfileOut(BaseModel):
    id: int
    username: str
    stats: ProfileStatsOut
    progress: ProfileProgressOut