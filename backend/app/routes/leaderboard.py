"""
Leaderboard route.

Joins User + UserStats directly (no new table, per assignment note).
Sort is xp_total DESC, then username ASC as a deterministic tiebreaker —
with one seeded user this only matters once you add more, but it makes
rank stable instead of depending on SQLite's default row order.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..dependencies import get_current_user
from ..schemas.leaderboard import LeaderboardOut, LeaderboardEntryOut

router = APIRouter(prefix="/api", tags=["leaderboard"])


@router.get("/leaderboard", response_model=LeaderboardOut)
def get_leaderboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    rows = (
        db.query(models.User, models.UserStats)
        .join(models.UserStats, models.UserStats.user_id == models.User.id)
        .order_by(models.UserStats.xp_total.desc(), models.User.username.asc())
        .all()
    )

    entries = []
    current_user_rank = 0
    for rank, (user, stats) in enumerate(rows, start=1):
        entries.append(LeaderboardEntryOut(rank=rank, username=user.username, xp=stats.xp_total))
        if user.id == current_user.id:
            current_user_rank = rank

    return LeaderboardOut(entries=entries, current_user_rank=current_user_rank)