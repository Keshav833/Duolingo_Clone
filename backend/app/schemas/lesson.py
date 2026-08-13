"""
Schemas for GET /api/lessons/{lesson_id}.

ExerciseOut deliberately has no `correct_answer` field. Pydantic only
serializes fields declared on the schema — since correct_answer isn't
declared here, model_validate(exercise) silently drops it even though the
underlying Exercise ORM object has it. The answer stays server-side for the
upcoming POST /api/lessons/{id}/answer endpoint to check against.
"""

from typing import List, Optional, Any

from pydantic import BaseModel, ConfigDict

from ..models import ExerciseType


class ExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order: int
    type: ExerciseType
    question: str
    options: Optional[Any] = None
    # No correct_answer field — this is intentional, not an oversight.


class LessonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order: int
    xp_reward: int
    exercises: List[ExerciseOut]