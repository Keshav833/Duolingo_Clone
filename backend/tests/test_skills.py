"""
Tests for GET /api/skills/{skill_id}/lessons.

Read-only route -> no state cleanup needed.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import Lesson

client = TestClient(app)


def _db():
    return SessionLocal()


def _first_skill_id_with_lessons() -> int:
    db = _db()
    lesson = db.query(Lesson).order_by(Lesson.skill_id).first()
    skill_id = lesson.skill_id
    db.close()
    return skill_id


def test_valid_skill_returns_200():
    skill_id = _first_skill_id_with_lessons()
    resp = client.get(f"/api/skills/{skill_id}/lessons")
    assert resp.status_code == 200


def test_skill_info_included():
    skill_id = _first_skill_id_with_lessons()
    data = client.get(f"/api/skills/{skill_id}/lessons").json()
    assert data["skill"]["id"] == skill_id
    assert "title" in data["skill"]
    assert "status" in data["skill"]


def test_lessons_present_and_ordered():
    skill_id = _first_skill_id_with_lessons()
    data = client.get(f"/api/skills/{skill_id}/lessons").json()
    orders = [lesson["order"] for lesson in data["lessons"]]
    assert orders == sorted(orders)
    assert len(data["lessons"]) > 0


def test_lesson_fields_are_minimal():
    skill_id = _first_skill_id_with_lessons()
    data = client.get(f"/api/skills/{skill_id}/lessons").json()
    for lesson in data["lessons"]:
        assert set(lesson.keys()) == {"id", "order", "xp_reward"}
        assert "exercises" not in lesson
        assert "correct_answer" not in lesson


def test_nonexistent_skill_returns_404():
    resp = client.get("/api/skills/99999/lessons")
    assert resp.status_code == 404


def test_existing_routes_still_work():
    assert client.get("/api/me").status_code == 200
    assert client.get("/api/course").status_code == 200
    assert client.get("/api/lessons/1").status_code == 200
    assert client.get("/api/profile").status_code == 200
    assert client.get("/api/leaderboard").status_code == 200