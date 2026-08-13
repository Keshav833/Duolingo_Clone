"""
Schemas for GET /api/course.

Note SkillOut has fields (status, crowns, lessons_completed) that don't
exist on the Skill ORM model — they live on UserSkillProgress. That's
intentional: this schema describes the shape of the *response*, not a
1:1 mirror of a table. The route below is what actually merges the two
sources before handing data to this schema.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from ..models import SkillStatus


class SkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    icon: Optional[str]
    order: int
    status: SkillStatus
    crowns: int
    lessons_completed: int


class UnitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    order: int
    skills: List[SkillOut]


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    language: str
    units: List[UnitOut]