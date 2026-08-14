"""
User-facing routes. Currently just /api/me — powers the top bar
(streak, XP, hearts, daily goal).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..dependencies import get_current_user
from ..hearts import apply_heart_regen
from ..schemas.user import UserOut

router = APIRouter(prefix="/api", tags=["user"])


@router.get("/me", response_model=UserOut)
def get_me(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Returns the current learner + their stats.

    Lazily applies heart regeneration before returning, since this is the
    route the frontend re-fetches fresh before allowing lesson entry (see
    the skill page's hearts > 0 check) — so it needs to reflect elapsed
    time, not just whatever was last written to the DB.

    response_model=UserOut does two things:
      1. Validates that `current_user` (a SQLAlchemy User object) actually
         has the shape UserOut expects.
      2. Strips anything not declared on UserOut before it's sent — so even
         though the User ORM object has a `created_at`, `skill_progress`,
         etc., the JSON response only contains what UserOut declares.
    """
    stats = current_user.stats
    before = (stats.hearts, stats.last_heart_lost_at)

    apply_heart_regen(stats)

    if (stats.hearts, stats.last_heart_lost_at) != before:
        db.commit()
        db.refresh(stats)

    return current_user