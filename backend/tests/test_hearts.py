"""
Tests for heart regeneration: app/hearts.py directly (cases A-E), plus its
integration into GET /api/me (case F) and POST /api/lessons/{id}/answer
(cases G-I).

Self-contained deliberately: this file doesn't assume any shared conftest
fixtures, since it's being added alongside an existing suite whose fixture
names weren't available when writing this. Each integration test snapshots
the seeded user's UserStats row and restores it in a `finally` block —
the same idea as _clean_skill_state() in test_complete.py, applied to
UserStats instead of UserSkillProgress, so the real seeded demo database
is never left in a mutated state after a test run.
"""

from contextlib import contextmanager
from datetime import datetime, timedelta, UTC

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import User, UserStats
from app.hearts import apply_heart_regen, REGEN_INTERVAL

client = TestClient(app)

CURRENT_USERNAME = "Keshav"


# ---------- shared helpers for the integration tests (F-I) ----------

@contextmanager
def _clean_stats_state():
    """Snapshot the seeded user's UserStats row, restore it after the test."""
    db = SessionLocal()
    user = db.query(User).filter(User.username == CURRENT_USERNAME).first()
    stats = user.stats
    snapshot = {
        "hearts": stats.hearts,
        "hearts_max": stats.hearts_max,
        "last_heart_lost_at": stats.last_heart_lost_at,
    }
    db.close()
    try:
        yield
    finally:
        db2 = SessionLocal()
        user2 = db2.query(User).filter(User.username == CURRENT_USERNAME).first()
        s2 = user2.stats
        s2.hearts = snapshot["hearts"]
        s2.hearts_max = snapshot["hearts_max"]
        s2.last_heart_lost_at = snapshot["last_heart_lost_at"]
        db2.commit()
        db2.close()


def _set_stats(hearts: int, minutes_ago, hearts_max: int = 5) -> None:
    db = SessionLocal()
    user = db.query(User).filter(User.username == CURRENT_USERNAME).first()
    stats = user.stats
    stats.hearts = hearts
    stats.hearts_max = hearts_max
    stats.last_heart_lost_at = (
        datetime.now(UTC) - timedelta(minutes=minutes_ago) if minutes_ago is not None else None
    )
    db.commit()
    db.close()


def _read_stats():
    db = SessionLocal()
    user = db.query(User).filter(User.username == CURRENT_USERNAME).first()
    stats = user.stats
    result = (stats.hearts, stats.last_heart_lost_at)
    db.close()
    return result


# ---------- A-E: apply_heart_regen unit tests (no DB, no app) ----------

def test_a_one_heart_regenerates_after_31_minutes():
    now = datetime.now(UTC)
    anchor = now - timedelta(minutes=31)
    stats = UserStats(hearts=0, hearts_max=5, last_heart_lost_at=anchor)

    apply_heart_regen(stats, now=now)

    assert stats.hearts == 1
    assert stats.last_heart_lost_at == anchor + REGEN_INTERVAL


def test_b_two_hearts_regenerate_after_61_minutes():
    now = datetime.now(UTC)
    anchor = now - timedelta(minutes=61)
    stats = UserStats(hearts=0, hearts_max=5, last_heart_lost_at=anchor)

    apply_heart_regen(stats, now=now)

    assert stats.hearts == 2
    assert stats.last_heart_lost_at == anchor + timedelta(minutes=60)


def test_c_hearts_cap_at_max_and_clear_timestamp():
    now = datetime.now(UTC)
    anchor = now - timedelta(minutes=31)
    stats = UserStats(hearts=4, hearts_max=5, last_heart_lost_at=anchor)

    apply_heart_regen(stats, now=now)

    assert stats.hearts == 5
    assert stats.last_heart_lost_at is None


def test_d_no_regen_before_cooldown():
    now = datetime.now(UTC)
    anchor = now - timedelta(minutes=10)
    stats = UserStats(hearts=0, hearts_max=5, last_heart_lost_at=anchor)

    apply_heart_regen(stats, now=now)

    assert stats.hearts == 0
    assert stats.last_heart_lost_at == anchor  # unchanged


def test_e_full_hearts_no_timestamp_no_change():
    now = datetime.now(UTC)
    stats = UserStats(hearts=5, hearts_max=5, last_heart_lost_at=None)

    apply_heart_regen(stats, now=now)

    assert stats.hearts == 5
    assert stats.last_heart_lost_at is None


# ---------- F: GET /api/me reflects regenerated hearts ----------

def test_f_get_me_reflects_regenerated_hearts():
    with _clean_stats_state():
        _set_stats(hearts=0, minutes_ago=31)

        r = client.get("/api/me")

        assert r.status_code == 200
        assert r.json()["stats"]["hearts"] == 1

        db_hearts, db_anchor = _read_stats()
        assert db_hearts == 1
        # Regen must be persisted, not just reflected in this one response.
        assert db_anchor is not None


# ---------- G: wrong answer after regen ----------

def test_g_wrong_answer_regenerates_then_consumes_one_heart():
    """
    hearts=0, 31 minutes elapsed -> regen brings hearts to 1 -> a wrong
    answer immediately consumes that 1 heart -> final hearts == 0.

    (Not 1 — regenerating exactly one heart and then losing exactly one
    heart nets to zero, not one.)
    """
    with _clean_stats_state():
        _set_stats(hearts=0, minutes_ago=31)

        r = client.post(
            "/api/lessons/1/answer",
            json={"exercise_id": 1, "submitted_answer": "definitely wrong"},
        )

        assert r.status_code == 200
        body = r.json()
        assert body["correct"] is False
        assert body["hearts"] == 0

        db_hearts, _ = _read_stats()
        assert db_hearts == 0


# ---------- H: first heart loss sets the timestamp ----------

def test_h_first_heart_loss_sets_timestamp():
    with _clean_stats_state():
        _set_stats(hearts=5, minutes_ago=None)

        r = client.post(
            "/api/lessons/1/answer",
            json={"exercise_id": 1, "submitted_answer": "definitely wrong"},
        )

        assert r.status_code == 200
        assert r.json()["hearts"] == 4

        _, anchor = _read_stats()
        assert anchor is not None


# ---------- I: subsequent heart loss does not reset the timestamp ----------

def test_i_subsequent_heart_loss_does_not_reset_timestamp():
    with _clean_stats_state():
        original_anchor = datetime.now(UTC) - timedelta(minutes=5)
        _set_stats(hearts=3, minutes_ago=5)  # anchor already set, 5 min ago

        r = client.post(
            "/api/lessons/1/answer",
            json={"exercise_id": 1, "submitted_answer": "definitely wrong"},
        )

        assert r.status_code == 200
        assert r.json()["hearts"] == 2

        _, anchor_after = _read_stats()
        if anchor_after.tzinfo is None:
            anchor_after = anchor_after.replace(tzinfo=UTC)
        # Must still be ~5 minutes ago, not reset to "now" by this 2nd loss.
        assert abs((anchor_after - original_anchor).total_seconds()) < 2