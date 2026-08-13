"""
Pydantic schemas = the FastAPI equivalent of the response shape you'd
hand-document in an Express API, except it's enforced automatically:
FastAPI validates the ORM object against this shape and rejects/serializes
accordingly. Think of it as a TypeScript interface that's also a runtime
validator.

model_config = ConfigDict(from_attributes=True) is what lets a schema be
built directly from a SQLAlchemy object (`UserOut.model_validate(user)`)
instead of a plain dict — without it, Pydantic won't read `.username` off
an ORM instance.
"""

from pydantic import BaseModel, ConfigDict


class UserStatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    xp_total: int
    streak_count: int
    hearts: int
    hearts_max: int
    daily_xp_goal: int
    daily_xp_earned: int


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    stats: UserStatsOut