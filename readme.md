# Duolingo Clone

A full-stack clone of Duolingo's core learning loop, built for the Scaler AI Labs Software Engineering Intern assignment.

**GitHub:** _add your repo link here_
**Live demo:** _add your deployment link here_

---

## Overview

The app implements one seeded course (Spanish for Beginners) with a skill tree, a lesson player supporting 5 exercise types, hearts/XP/streak gamification with server-side heart regeneration, a profile page, and a leaderboard — all backed by a real relational schema rather than mocked/hardcoded data.

The backend is authoritative for all gameplay state (XP, hearts, streak, skill unlocking). The frontend renders what the backend returns and never computes gameplay outcomes itself.

## Tech stack

| Layer    | Technology                          |
|----------|--------------------------------------|
| Frontend | Next.js (App Router) + TypeScript   |
| Backend  | FastAPI + Python                    |
| ORM      | SQLAlchemy 2.0                      |
| Database | SQLite                              |
| Testing  | pytest                              |

## Project structure

```
duolingo-clone/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, router registration
│   │   ├── database.py        # SQLAlchemy engine/session setup
│   │   ├── models.py          # ORM models — the full schema
│   │   ├── dependencies.py    # get_current_user (single seeded learner)
│   │   ├── hearts.py          # heart regeneration logic
│   │   ├── seed.py            # populates demo course + user
│   │   ├── routes/            # one file per resource
│   │   └── schemas/           # Pydantic request/response models
│   ├── scripts/
│   │   └── reset_demo_progress.py   # one-time dev reset utility
│   ├── tests/                 # pytest suite
│   └── venv/
├── frontend/
│   ├── app/
│   │   ├── page.tsx                    # dashboard (skill tree)
│   │   ├── skill/[skillId]/page.tsx    # lessons within a skill
│   │   ├── lesson/[lessonId]/page.tsx  # lesson player
│   │   ├── profile/page.tsx
│   │   └── leaderboard/page.tsx
│   └── lib/
│       ├── api.ts             # shared fetch helper
│       └── types.ts           # shared TS types matching backend schemas
└── README.md
```

## Getting started

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt   # fastapi, uvicorn, sqlalchemy, pydantic, pytest

python -m app.seed                # populate the database (safe to re-run — drops & recreates)
uvicorn app.main:app --reload     # http://localhost:8000
```

Interactive API docs (auto-generated from the Pydantic schemas): `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev                   # http://localhost:3000
```

The backend's CORS config allows `http://localhost:3000` specifically — update `backend/app/main.py` if the frontend runs elsewhere.

## Authentication

The assignment allows simplifying auth to a single default learner. There is no login flow — every request acts as the seeded user (`username = "Keshav"`), resolved via a single `get_current_user` dependency (`backend/app/dependencies.py`) rather than a hardcoded ID scattered through the routes, so real auth can be swapped in later by changing one function.

## Database schema

Two halves, kept deliberately separate:

**Static content** (seeded once, shared by all users):
```
Course → Unit → Skill → Lesson → Exercise
```

**Per-user state:**
```
User ── UserStats            (1:1 — xp, streak, hearts, daily goal)
     ── UserSkillProgress    (1:N — status/crowns per skill)
     ── UserLessonProgress   (1:N — completion/xp per lesson)
```

`Exercise.options` / `Exercise.correct_answer` are JSON columns so one table covers all 5 exercise types instead of five separate tables — the `type` column tells the frontend how to render it and the backend how to grade it. See the top of `models.py` for the exact JSON shape per type.

## Seeded content

- 1 course: **Spanish for Beginners**
- 2 units, 4 skills (Greetings, Introductions, Food, Family), 8 lessons
- 40 exercises — 5 per lesson, one of each required type (multiple choice, translate/word-bank, match pairs, fill-in-the-blank, type-answer)
- 1 demo learner with realistic in-progress state: Greetings completed, Introductions available, Food and Family locked

Re-seed anytime with `python -m app.seed` — it drops and recreates all tables, so it's safe to run repeatedly during development but will wipe any manual testing state.

## API reference

All routes are prefixed `/api`. Full request/response shapes are documented in `backend/app/schemas/` and browsable live at `/docs`.

| Method | Route                              | Purpose                                                        |
|--------|-------------------------------------|------------------------------------------------------------------|
| GET    | `/api/me`                          | Current learner + stats (xp, streak, hearts, daily goal). Applies heart regeneration on read. |
| GET    | `/api/course`                      | Full skill tree, merging static course content with the learner's per-skill progress. |
| GET    | `/api/skills/{skill_id}/lessons`   | A skill's lesson list (id/order/xp only — no exercise content). |
| GET    | `/api/lessons/{lesson_id}`         | A lesson's exercises. `correct_answer` is never included in this response. |
| POST   | `/api/lessons/{lesson_id}/answer`  | Submits one exercise answer. Validates server-side by exercise type, decrements hearts on a miss (floored at 0, never negative), returns the correct answer only after submission. |
| POST   | `/api/lessons/{lesson_id}/complete`| Marks a lesson complete: awards XP, updates streak, updates skill progress/crowns, unlocks the next skill when the current one is finished. Idempotent — re-completing an already-completed lesson awards no additional XP. |
| GET    | `/api/profile`                     | Learner stats + aggregate progress (skills/lessons completed). |
| GET    | `/api/leaderboard`                 | Seeded users ranked by XP descending (username as tie-breaker). |

### Why answers aren't returned with the lesson

`GET /api/lessons/{id}` intentionally omits `correct_answer` — it's stripped by the Pydantic response schema, not filtered manually, so it can't be accidentally leaked later. The answer only ever comes back from `POST .../answer`, after a submission, and only for that one exercise. This was a deliberate check during development: sending the answer key up front would let anyone read it from DevTools before answering.

## Gameplay mechanics

- **XP & streak**: awarded once per lesson (first completion only). Streak increments once per calendar day of activity, resets after a gap of more than one day.
- **Skill unlocking**: completing every lesson in a skill marks it `completed` and flips the next skill in course order from `locked` to `available`.
- **Hearts**: start at 5 (max 5), lose 1 per wrong answer, floored at 0. Regenerate 1 heart every 30 minutes while below max — computed lazily and backend-authoritatively (`backend/app/hearts.py`) whenever `/api/me` or the answer endpoint is called, using an anchor timestamp rather than a client-side timer, so the frontend never invents its own heart count.
- **Gems**: UI-only placeholder (static `💎 500`), not persisted — the assignment allows mocking purchases/currency, so there's no backend field or earn/spend logic for it.

## Testing

```bash
cd backend
venv\Scripts\activate
python -m pytest -v
```

Tests use the project's real SQLite database rather than a separate test DB; any test that mutates shared state (skill progress, hearts, stats) snapshots the affected rows beforehand and restores them in a `finally` block, so the seeded demo state is never left corrupted by a test run.

## Development scripts

- `backend/app/seed.py` — full reset + repopulate (course, units, skills, lessons, exercises, demo user, demo progress). Destructive: drops all tables first.
- `backend/scripts/reset_demo_progress.py` — one-time utility to reset the demo user's skill/lesson progress back to a fresh starting state (Greetings available, everything else locked) **without** touching XP, hearts, streak, or daily goal. Useful for re-recording a demo without a full re-seed.

## Known limitations / intentionally out of scope

Per the assignment, these were deliberately left as placeholders rather than built out:
- No real authentication (single hardcoded seeded learner)
- No real purchases / Super subscription (gems are static UI only)
- No speech recognition, audio, or multiple languages
- No friends/social features or achievements
- No dark mode

## Development approach

Built with AI-assisted implementation throughout (permitted and encouraged by the assignment), with the design decisions — schema shape, API contract, gamification rules — made first and reviewed at each step rather than generating the whole app in one pass. Every endpoint was manually tested end-to-end (success paths, error paths, edge cases like hearts flooring at zero and double-completion not double-awarding XP) before being considered done.
