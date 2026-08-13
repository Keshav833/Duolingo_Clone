from contextlib import contextmanager
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import Lesson, UserStats, UserLessonProgress, UserSkillProgress, SkillStatus, Skill

client = TestClient(app)

USER_ID = 1  # Keshav, seeded


def _db():
    return SessionLocal()


def _copy_lesson_progress(lp: UserLessonProgress | None) -> dict | None:
    if lp is None:
        return None
    return {
        "user_id": lp.user_id,
        "lesson_id": lp.lesson_id,
        "completed": lp.completed,
        "xp_earned": lp.xp_earned,
        "accuracy": lp.accuracy,
        "completed_at": lp.completed_at,
    }


def _copy_skill_progress(sp: UserSkillProgress | None) -> dict | None:
    if sp is None:
        return None
    return {
        "user_id": sp.user_id,
        "skill_id": sp.skill_id,
        "status": sp.status,
        "crowns": sp.crowns,
        "lessons_completed": sp.lessons_completed,
    }


@contextmanager
def _clean_skill_state(skill_id: int):
    """
    Temporarily wipes UserSkillProgress and every UserLessonProgress row
    belonging to this skill, so a test starts from a genuinely clean slate
    (not just the one lesson it's about to complete). On exit, restores the
    original rows exactly, so seeded demo state -- Greetings completed,
    Introductions available, Food/Family locked -- survives the test run.

    Yields the list of lesson_ids that belong to this skill, in case a test
    needs to complete more than one of them.
    """
    db = _db()
    lesson_ids = [
        row.id for row in db.query(Lesson).filter(Lesson.skill_id == skill_id).all()
    ]

    saved_skill = _copy_skill_progress(
        db.query(UserSkillProgress)
        .filter(
            UserSkillProgress.user_id == USER_ID,
            UserSkillProgress.skill_id == skill_id,
        )
        .first()
    )

    saved_lessons = [
        _copy_lesson_progress(lp)
        for lp in db.query(UserLessonProgress)
        .filter(
            UserLessonProgress.user_id == USER_ID,
            UserLessonProgress.lesson_id.in_(lesson_ids),
        )
        .all()
    ]

    db.query(UserLessonProgress).filter(
        UserLessonProgress.user_id == USER_ID,
        UserLessonProgress.lesson_id.in_(lesson_ids),
    ).delete(synchronize_session=False)
    db.query(UserSkillProgress).filter(
        UserSkillProgress.user_id == USER_ID,
        UserSkillProgress.skill_id == skill_id,
    ).delete(synchronize_session=False)
    db.commit()
    db.close()

    try:
        yield lesson_ids
    finally:
        db = _db()
        db.query(UserLessonProgress).filter(
            UserLessonProgress.user_id == USER_ID,
            UserLessonProgress.lesson_id.in_(lesson_ids),
        ).delete(synchronize_session=False)
        db.query(UserSkillProgress).filter(
            UserSkillProgress.user_id == USER_ID,
            UserSkillProgress.skill_id == skill_id,
        ).delete(synchronize_session=False)
        db.commit()

        for data in saved_lessons:
            db.add(UserLessonProgress(**data))
        if saved_skill is not None:
            db.add(UserSkillProgress(**saved_skill))
        db.commit()
        db.close()


def _set_stats(streak=0, last_activity_date=None, xp_total=None, daily_xp_earned=0):
    """last_activity_date must be a datetime (or None), matching the DateTime column."""
    db = _db()
    stats = db.query(UserStats).filter(UserStats.user_id == USER_ID).first()
    stats.streak_count = streak
    stats.last_activity_date = last_activity_date
    stats.daily_xp_earned = daily_xp_earned
    if xp_total is not None:
        stats.xp_total = xp_total
    db.commit()
    db.close()


def _skill_id_for_lesson(lesson_id: int) -> int:
    db = _db()
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    skill_id = lesson.skill_id
    db.close()
    return skill_id


def test_complete_incomplete_lesson():
    skill_id = _skill_id_for_lesson(1)
    with _clean_skill_state(skill_id):
        _set_stats(streak=0, last_activity_date=None, daily_xp_earned=0)

        resp = client.post("/api/lessons/1/complete")
        assert resp.status_code == 200
        data = resp.json()

        assert data["lesson_completed"] is True
        assert data["already_completed"] is False
        assert data["xp_earned"] > 0
        assert data["skill"]["lessons_completed"] == 1
        assert data["skill"]["crowns"] == 1


def test_complete_same_lesson_twice_no_double_xp():
    skill_id = _skill_id_for_lesson(1)
    with _clean_skill_state(skill_id):
        _set_stats(streak=0, last_activity_date=None, daily_xp_earned=0)

        first = client.post("/api/lessons/1/complete").json()
        second = client.post("/api/lessons/1/complete").json()

        assert second["already_completed"] is True
        assert second["xp_earned"] == 0
        assert second["total_xp"] == first["total_xp"]
        assert second["skill"]["lessons_completed"] == first["skill"]["lessons_completed"]
        assert second["streak"] == first["streak"]


def test_xp_equals_lesson_reward():
    skill_id = _skill_id_for_lesson(2)
    with _clean_skill_state(skill_id):
        resp = client.post("/api/lessons/2/complete").json()
        lesson_resp = client.get("/api/lessons/2").json()
        assert resp["xp_earned"] == lesson_resp["xp_reward"]


def test_same_day_completion_does_not_increase_streak():
    today_dt = datetime.utcnow()
    skill_id = _skill_id_for_lesson(3)
    with _clean_skill_state(skill_id):
        _set_stats(streak=5, last_activity_date=today_dt)
        resp = client.post("/api/lessons/3/complete").json()
        assert resp["streak"] == 5


def test_yesterday_to_today_increments_streak():
    yesterday_dt = datetime.utcnow() - timedelta(days=1)
    skill_id = _skill_id_for_lesson(4)
    with _clean_skill_state(skill_id):
        _set_stats(streak=5, last_activity_date=yesterday_dt)
        resp = client.post("/api/lessons/4/complete").json()
        assert resp["streak"] == 6


def test_gap_of_more_than_one_day_resets_streak():
    old_dt = datetime.utcnow() - timedelta(days=3)
    skill_id = _skill_id_for_lesson(5)
    with _clean_skill_state(skill_id):
        _set_stats(streak=8, last_activity_date=old_dt)
        resp = client.post("/api/lessons/5/complete").json()
        assert resp["streak"] == 1


def test_nonexistent_lesson_returns_404():
    resp = client.post("/api/lessons/99999/complete")
    assert resp.status_code == 404


def test_existing_routes_still_work():
    assert client.get("/api/me").status_code == 200
    assert client.get("/api/course").status_code == 200
    assert client.get("/api/lessons/1").status_code == 200

def test_completing_all_lessons_completes_skill_and_unlocks_next():
    """
    Completing every lesson in a skill should:
    - mark the current skill completed
    - unlock the next skill
    """
    db = _db()

    # Get the first two skills in course order.
    skills = (
        db.query(Skill)
        .order_by(Skill.id)
        .limit(2)
        .all()
    )

    current_skill = skills[0]
    next_skill = skills[1]

    # Get every lesson belonging to the current skill.
    lessons = (
        db.query(Lesson)
        .filter(Lesson.skill_id == current_skill.id)
        .order_by(Lesson.order)
        .all()
    )

    lesson_ids = [lesson.id for lesson in lessons]

    db.close()

    with _clean_skill_state(current_skill.id):
        # Make sure the next skill starts locked.
        db = _db()
        next_progress = (
            db.query(UserSkillProgress)
            .filter(
                UserSkillProgress.user_id == USER_ID,
                UserSkillProgress.skill_id == next_skill.id,
            )
            .first()
        )

        if next_progress is None:
            next_progress = UserSkillProgress(
                user_id=USER_ID,
                skill_id=next_skill.id,
                status=SkillStatus.locked,
                crowns=0,
                lessons_completed=0,
            )
            db.add(next_progress)
        else:
            next_progress.status = SkillStatus.locked

        db.commit()
        db.close()

        # Complete every lesson in the current skill.
        for lesson_id in lesson_ids:
            response = client.post(
                f"/api/lessons/{lesson_id}/complete"
            )
            assert response.status_code == 200

        # Verify current skill is completed.
        db = _db()

        current_progress = (
            db.query(UserSkillProgress)
            .filter(
                UserSkillProgress.user_id == USER_ID,
                UserSkillProgress.skill_id == current_skill.id,
            )
            .first()
        )

        next_progress = (
            db.query(UserSkillProgress)
            .filter(
                UserSkillProgress.user_id == USER_ID,
                UserSkillProgress.skill_id == next_skill.id,
            )
            .first()
        )

        assert current_progress is not None
        assert current_progress.status == SkillStatus.completed
        assert current_progress.lessons_completed == len(lessons)

        assert next_progress is not None
        assert next_progress.status == SkillStatus.available

        db.close()


def test_completing_only_part_of_skill_does_not_unlock_next():
    """
    Completing only some lessons in a skill should NOT complete the skill
    or unlock the next skill.
    """
    db = _db()

    skills = (
        db.query(Skill)
        .order_by(Skill.id)
        .limit(2)
        .all()
    )

    current_skill = skills[0]
    next_skill = skills[1]

    lessons = (
        db.query(Lesson)
        .filter(Lesson.skill_id == current_skill.id)
        .order_by(Lesson.order)
        .all()
    )

    # This test requires the skill to have more than one lesson.
    assert len(lessons) > 1

    first_lesson_id = lessons[0].id

    db.close()

    with _clean_skill_state(current_skill.id):
        # Make sure the next skill starts locked.
        db = _db()

        next_progress = (
            db.query(UserSkillProgress)
            .filter(
                UserSkillProgress.user_id == USER_ID,
                UserSkillProgress.skill_id == next_skill.id,
            )
            .first()
        )

        if next_progress is None:
            next_progress = UserSkillProgress(
                user_id=USER_ID,
                skill_id=next_skill.id,
                status=SkillStatus.locked,
                crowns=0,
                lessons_completed=0,
            )
            db.add(next_progress)
        else:
            next_progress.status = SkillStatus.locked

        db.commit()
        db.close()

        # Complete only the first lesson.
        response = client.post(
            f"/api/lessons/{first_lesson_id}/complete"
        )

        assert response.status_code == 200

        # Verify current skill is NOT completed and next skill is locked.
        db = _db()

        current_progress = (
            db.query(UserSkillProgress)
            .filter(
                UserSkillProgress.user_id == USER_ID,
                UserSkillProgress.skill_id == current_skill.id,
            )
            .first()
        )

        next_progress = (
            db.query(UserSkillProgress)
            .filter(
                UserSkillProgress.user_id == USER_ID,
                UserSkillProgress.skill_id == next_skill.id,
            )
            .first()
        )

        assert current_progress is not None
        assert current_progress.status != SkillStatus.completed
        assert current_progress.lessons_completed == 1

        assert next_progress is not None
        assert next_progress.status == SkillStatus.locked

        db.close()