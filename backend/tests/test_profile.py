"""
Tests for GET /api/profile.

Read-only route -> no _clean_skill_state isolation needed here (nothing is
mutated). Progress counts are computed directly from the DB in each test
and compared against the API response, rather than hardcoded, so these
tests don't depend on what order test_complete.py's tests happened to run in.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import UserSkillProgress, UserLessonProgress, SkillStatus

client = TestClient(app)

USER_ID = 1  # Keshav, seeded


def _db():
    return SessionLocal()


def _expected_progress_counts():
    db = _db()
    skills_completed = (
        db.query(UserSkillProgress)
        .filter(
            UserSkillProgress.user_id == USER_ID,
            UserSkillProgress.status == SkillStatus.completed,
        )
        .count()
    )
    lessons_completed = (
        db.query(UserLessonProgress)
        .filter(
            UserLessonProgress.user_id == USER_ID,
            UserLessonProgress.completed == True,  # noqa: E712 (SQLAlchemy filter, not Python identity)
        )
        .count()
    )
    db.close()
    return skills_completed, lessons_completed


def test_profile_returns_200():
    resp = client.get("/api/profile")
    assert resp.status_code == 200


def test_profile_username_is_keshav():
    data = client.get("/api/profile").json()
    assert data["username"] == "Keshav"
    assert data["id"] == USER_ID


def test_profile_stats_returned():
    data = client.get("/api/profile").json()
    stats = data["stats"]
    for field in (
        "xp_total",
        "streak_count",
        "hearts",
        "hearts_max",
        "daily_xp_goal",
        "daily_xp_earned",
    ):
        assert field in stats


def test_profile_progress_counts_match_db():
    expected_skills, expected_lessons = _expected_progress_counts()
    data = client.get("/api/profile").json()
    assert data["progress"]["skills_completed"] == expected_skills
    assert data["progress"]["lessons_completed"] == expected_lessons


def test_me_still_works():
    assert client.get("/api/me").status_code == 200


def test_course_still_works():
    assert client.get("/api/course").status_code == 200