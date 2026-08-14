"""
Tests for GET /api/leaderboard.

Read-only route -> no state cleanup needed. Seed data now includes four
users (Keshav + 3 others) so these tests exercise real multi-user ranking,
not just the single-entry case. The ordering/rank-sequencing checks are
written generically against len(entries), so they hold regardless of how
many users are seeded.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

USER_ID = 1  # Keshav, seeded


def test_leaderboard_returns_200():
    resp = client.get("/api/leaderboard")
    assert resp.status_code == 200


def test_leaderboard_entries_ordered_by_xp_descending():
    entries = client.get("/api/leaderboard").json()["entries"]
    xp_values = [e["xp"] for e in entries]
    assert xp_values == sorted(xp_values, reverse=True)


def test_leaderboard_rank_starts_at_one_and_is_sequential():
    entries = client.get("/api/leaderboard").json()["entries"]
    ranks = [e["rank"] for e in entries]
    assert ranks == list(range(1, len(entries) + 1))


def test_leaderboard_current_user_rank_returned():
    data = client.get("/api/leaderboard").json()
    assert data["current_user_rank"] >= 1
    # current_user_rank must correspond to an entry actually belonging to Keshav
    matching = [e for e in data["entries"] if e["rank"] == data["current_user_rank"]]
    assert len(matching) == 1
    assert matching[0]["username"] == "Keshav"


def test_existing_routes_still_work():
    assert client.get("/api/me").status_code == 200
    assert client.get("/api/course").status_code == 200
    assert client.get("/api/lessons/1").status_code == 200


def test_leaderboard_has_multiple_seeded_users():
    entries = client.get("/api/leaderboard").json()["entries"]
    assert len(entries) > 1


def test_all_seeded_usernames_present():
    entries = client.get("/api/leaderboard").json()["entries"]
    usernames = {e["username"] for e in entries}
    assert {"Keshav", "Aarav", "Priya", "Rahul"}.issubset(usernames)