"""
User-facing routes. Currently just /api/me — powers the top bar
(streak, XP, hearts, daily goal).
"""

from fastapi import APIRouter, Depends

from .. import models
from ..dependencies import get_current_user
from ..schemas.user import UserOut

router = APIRouter(prefix="/api", tags=["user"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: models.User = Depends(get_current_user)):
    """
    Returns the current learner + their stats.

    response_model=UserOut does two things:
      1. Validates that `current_user` (a SQLAlchemy User object) actually
         has the shape UserOut expects.
      2. Strips anything not declared on UserOut before it's sent — so even
         though the User ORM object has a `created_at`, `skill_progress`,
         etc., the JSON response only contains what UserOut declares.
    """
    return current_user