# backend/tests/test_answer.py
#
# Run with: pytest tests/test_answer.py -v
# Assumes your seeded DB (python -m app.seed) has already been run once,
# same as your existing /api/course tests.

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Lesson, Exercise, UserStats, User

client = TestClient(app)


def _get_lesson_and_exercises():
    """Pull the first seeded lesson and its exercises directly from the DB
    so tests aren't hardcoding IDs that might differ across seed runs."""
    db = SessionLocal()
    lesson = db.query(Lesson).order_by(Lesson.id).first()
    exercises = db.query(Exercise).filter(Exercise.lesson_id == lesson.id).all()
    by_type = {e.type: e for e in exercises}
    db.close()
    return lesson, by_type


def _reset_hearts():
    db = SessionLocal()
    user = db.query(User).first()
    stats = db.query(UserStats).filter(UserStats.user_id == user.id).first()
    stats.hearts = stats.hearts_max
    db.commit()
    db.close()


def test_correct_mcq():
    _reset_hearts()
    lesson, ex = _get_lesson_and_exercises()
    e = ex["multiple_choice"]
    correct_value = e.correct_answer["correct"]
    r = client.post(f"/api/lessons/{lesson.id}/answer",
                     json={"exercise_id": e.id, "submitted_answer": correct_value})
    assert r.status_code == 200
    assert r.json()["correct"] is True


def test_wrong_mcq():
    _reset_hearts()
    lesson, ex = _get_lesson_and_exercises()
    e = ex["multiple_choice"]
    before = client.get("/api/me").json()["stats"]["hearts"]
    r = client.post(f"/api/lessons/{lesson.id}/answer",
                     json={"exercise_id": e.id, "submitted_answer": "__definitely_wrong__"})
    assert r.status_code == 200
    body = r.json()
    assert body["correct"] is False
    assert body["hearts"] == before - 1


def test_correct_type_answer():
    _reset_hearts()
    lesson, ex = _get_lesson_and_exercises()
    e = ex["type_answer"]
    correct_value = e.correct_answer["correct"]
    r = client.post(f"/api/lessons/{lesson.id}/answer",
                     json={"exercise_id": e.id, "submitted_answer": correct_value})
    assert r.json()["correct"] is True


def test_wrong_type_answer():
    _reset_hearts()
    lesson, ex = _get_lesson_and_exercises()
    e = ex["type_answer"]
    r = client.post(f"/api/lessons/{lesson.id}/answer",
                     json={"exercise_id": e.id, "submitted_answer": "__wrong__"})
    assert r.json()["correct"] is False


def test_translate_correct_and_wrong():
    _reset_hearts()
    lesson, ex = _get_lesson_and_exercises()
    e = ex["translate"]
    correct_value = e.correct_answer["correct"]

    r = client.post(f"/api/lessons/{lesson.id}/answer",
                     json={"exercise_id": e.id, "submitted_answer": correct_value})
    assert r.json()["correct"] is True

    _reset_hearts()
    scrambled = list(reversed(correct_value))
    r = client.post(f"/api/lessons/{lesson.id}/answer",
                     json={"exercise_id": e.id, "submitted_answer": scrambled})
    assert r.json()["correct"] is False


def test_match_pairs_correct_and_wrong():
    _reset_hearts()
    lesson, ex = _get_lesson_and_exercises()
    e = ex["match_pairs"]
    correct_value = e.correct_answer

    r = client.post(f"/api/lessons/{lesson.id}/answer",
                     json={"exercise_id": e.id, "submitted_answer": correct_value})
    assert r.json()["correct"] is True

    _reset_hearts()
    broken = {k: "wrong" for k in correct_value}
    r = client.post(f"/api/lessons/{lesson.id}/answer",
                     json={"exercise_id": e.id, "submitted_answer": broken})
    assert r.json()["correct"] is False


def test_fill_blank():
    _reset_hearts()
    lesson, ex = _get_lesson_and_exercises()
    e = ex["fill_blank"]
    correct_value = e.correct_answer["correct"]
    r = client.post(f"/api/lessons/{lesson.id}/answer",
                     json={"exercise_id": e.id, "submitted_answer": correct_value})
    assert r.json()["correct"] is True


def test_hearts_never_go_below_zero():
    _reset_hearts()
    lesson, ex = _get_lesson_and_exercises()
    e = ex["type_answer"]
    for _ in range(10):
        r = client.post(f"/api/lessons/{lesson.id}/answer",
                         json={"exercise_id": e.id, "submitted_answer": "__wrong__"})
    assert r.json()["hearts"] == 0
    _reset_hearts()


def test_exercise_from_another_lesson_rejected():
    db = SessionLocal()
    lessons = db.query(Lesson).order_by(Lesson.id).all()
    lesson_a, lesson_b = lessons[0], lessons[1]
    exercise_in_b = db.query(Exercise).filter(Exercise.lesson_id == lesson_b.id).first()
    db.close()

    r = client.post(f"/api/lessons/{lesson_a.id}/answer",
                     json={"exercise_id": exercise_in_b.id, "submitted_answer": "x"})
    assert r.status_code == 400


def test_nonexistent_exercise_404():
    lesson, _ = _get_lesson_and_exercises()
    r = client.post(f"/api/lessons/{lesson.id}/answer",
                     json={"exercise_id": 999999, "submitted_answer": "x"})
    assert r.status_code == 404


def test_nonexistent_lesson_404():
    r = client.post("/api/lessons/999999/answer",
                     json={"exercise_id": 1, "submitted_answer": "x"})
    assert r.status_code == 404


# --- regression checks: existing endpoints must still work ---

def test_me_still_works():
    r = client.get("/api/me")
    assert r.status_code == 200


def test_course_still_works():
    r = client.get("/api/course")
    assert r.status_code == 200


def test_lesson_get_still_works():
    lesson, _ = _get_lesson_and_exercises()
    r = client.get(f"/api/lessons/{lesson.id}")
    assert r.status_code == 200
    # answer key must never leak from the GET endpoint
    for exercise in r.json()["exercises"]:
        assert "correct_answer" not in exercise