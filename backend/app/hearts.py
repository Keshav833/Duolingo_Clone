"""
Heart regeneration.

Single shared helper so GET /api/me and POST /api/lessons/{id}/answer never
diverge on how "current hearts, accounting for elapsed time" is computed.
Deliberately a flat module under app/, not a services/ package — one
function doesn't earn a new architectural layer.
"""

from datetime import datetime, timedelta, UTC

from app.models import UserStats

REGEN_INTERVAL = timedelta(minutes=30)


def apply_heart_regen(stats: UserStats, now: datetime | None = None) -> None:
    """
    Mutates stats.hearts / stats.last_heart_lost_at in place based on
    elapsed time since the last heart was lost. Does NOT commit — the
    caller owns the transaction.

    Rules:
      - Already at hearts_max -> clear last_heart_lost_at (nothing to
        anchor), no regen needed.
      - No last_heart_lost_at -> nothing to regenerate from.
      - Regenerate floor(elapsed / 30min) hearts, capped at hearts_max.
      - Anchor advances by (regenerated * 30min) rather than resetting to
        `now`, so leftover partial progress toward the next heart isn't
        thrown away.
      - If the cap is hit, clear last_heart_lost_at (full bar, no pending
        countdown).
    """
    if now is None:
        now = datetime.now(UTC)

    if stats.hearts >= stats.hearts_max:
        stats.last_heart_lost_at = None
        return

    if stats.last_heart_lost_at is None:
        return

    last_lost = stats.last_heart_lost_at
    # SQLite drops tzinfo on round-trip, so a value read back from the DB
    # is naive even though we always write it as UTC-aware. Treat naive
    # timestamps as UTC so the subtraction below is always valid.
    if last_lost.tzinfo is None:
        last_lost = last_lost.replace(tzinfo=UTC)

    elapsed = now - last_lost
    if elapsed < REGEN_INTERVAL:
        return

    regenerated = int(elapsed // REGEN_INTERVAL)
    if regenerated <= 0:
        return

    new_hearts = min(stats.hearts + regenerated, stats.hearts_max)
    stats.hearts = new_hearts

    if stats.hearts >= stats.hearts_max:
        stats.last_heart_lost_at = None
    else:
        stats.last_heart_lost_at = last_lost + (REGEN_INTERVAL * regenerated)