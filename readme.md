# Duolingo Clone

A full-stack Duolingo-inspired language learning application built as part of the Scaler AI Labs Software Engineering Intern assignment.

The project currently includes a FastAPI backend with SQLite, SQLAlchemy, user progress tracking, lessons, exercises, XP, streaks, hearts, skill progression, profile statistics, and a leaderboard.

---

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Pytest
- Uvicorn

### Frontend

- Next.js
- React
- TypeScript

---

## Project Structure

```text
Duolingo_Clone/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── dependencies.py
│   │   ├── seed.py
│   │   │
│   │   ├── routes/
│   │   │   ├── user.py
│   │   │   ├── course.py
│   │   │   ├── lessons.py
│   │   │   ├── answer.py
│   │   │   ├── complete.py
│   │   │   ├── profile.py
│   │   │   └── leaderboard.py
│   │   │
│   │   └── schemas/
│   │       ├── user.py
│   │       ├── course.py
│   │       ├── lesson.py
│   │       ├── answer.py
│   │       ├── complete.py
│   │       ├── profile.py
│   │       └── leaderboard.py
│   │
│   ├── tests/
│   │   ├── test_answer.py
│   │   ├── test_complete.py
│   │   ├── test_profile.py
│   │   └── test_leaderboard.py
│   │
│   ├── requirements.txt
│   └── duolingo.db
│
├── frontend/
│   └── ...
│
└── README.md
```

---

## Backend Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd Duolingo_Clone
```

### 2. Create a virtual environment

From the `backend` directory:

```bash
cd backend
python -m venv venv
```

### 3. Activate the virtual environment

**Windows**
```bash
venv\Scripts\activate
```

**macOS/Linux**
```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

## Database Setup

The backend uses SQLite with SQLAlchemy.

From the `backend` directory, with the virtual environment activated:

```bash
python -m app.seed
```

The seed script creates the initial course content and demo user.

The seeded dataset contains:

- 1 course
- 2 units
- 4 skills
- 8 lessons
- 40 exercises
- 1 demo user

---

## Running the Backend

From the `backend` directory:

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

```
http://localhost:8000
```

The root endpoint:

```
http://localhost:8000/
```

FastAPI interactive API documentation:

```
http://localhost:8000/docs
```

---

## API Documentation

### User

**Get Current User**
```
GET /api/me
```
Returns the current user's basic information and statistics.

### Course

**Get Course**
```
GET /api/course
```
Returns the course structure including units, skills, and user-specific skill progress.

### Lessons

**Get Lesson**
```
GET /api/lessons/{lesson_id}
```
Returns a lesson and its exercises.

The `correct_answer` is intentionally excluded from the response so that answer keys are not exposed to the client.

### Answer Submission

**Submit Exercise Answer**
```
POST /api/lessons/{lesson_id}/answer
```

Example request:

```json
{
  "exercise_id": 1,
  "submitted_answer": "Hello"
}
```

The answer is evaluated server-side.

For incorrect answers, the user's hearts are decremented. Hearts cannot go below zero.

The API supports the seeded exercise types:

- Multiple choice
- Translation
- Match pairs
- Fill in the blank
- Type answer

### Lesson Completion

**Complete Lesson**
```
POST /api/lessons/{lesson_id}/complete
```

Completing a lesson updates the relevant user progress, including:

- Lesson completion
- XP
- Daily XP
- Streak
- Skill progress
- Skill crowns
- Next skill unlock status

Completing the same lesson again does not award XP twice.

### Profile

**Get Profile**
```
GET /api/profile
```

Returns:

- Username
- XP
- Streak
- Hearts
- Maximum hearts
- Daily XP goal
- Daily XP earned
- Completed skills
- Completed lessons

### Leaderboard

**Get Leaderboard**
```
GET /api/leaderboard
```

Returns users ordered by XP in descending order and includes the current user's rank.

---

## Database Design

The database separates static course content from user-specific progress.

```
Course
  └── Unit
        └── Skill
              └── Lesson
                    └── Exercise

User
  ├── UserStats
  ├── UserSkillProgress
  └── UserLessonProgress
```

### Static Content

The following entities represent shared course content:

- Course
- Unit
- Skill
- Lesson
- Exercise

### User State

The following entities represent user-specific state:

- User
- UserStats
- UserSkillProgress
- UserLessonProgress

This separation allows course content to be shared while progress remains specific to each user.

### Exercise Data Model

Exercises use a common JSON-based structure so that multiple exercise types can be stored in a single `Exercise` table.

Supported types:

- multiple_choice
- translate
- match_pairs
- fill_blank
- type_answer

The exercise type determines how the frontend renders and submits the exercise.

The correct answer is stored server-side and is not returned by the lesson API.

---

## CORS

The backend currently allows requests from the local Next.js development server:

```
http://localhost:3000
```

This allows the frontend to communicate with the FastAPI backend during local development.

---

## Testing

The backend uses Pytest.

From the `backend` directory:

```bash
python -m pytest -v
```

The current test suite covers:

- Exercise answer validation
- Multiple exercise types
- Heart deduction
- Heart minimum of zero
- Invalid lesson handling
- Invalid exercise handling
- Cross-lesson exercise validation
- Lesson completion
- Duplicate lesson completion
- XP calculation
- Streak calculation
- Skill completion
- Skill unlocking
- Profile statistics
- Leaderboard ordering
- Leaderboard ranking
- Existing route regression checks

**Current test status:**

```
35 passed
```

---

## Current Development Status

### Backend

- [x] Database schema
- [x] Database seeding
- [x] User API
- [x] Course API
- [x] Lesson API
- [x] Answer submission
- [x] Lesson completion
- [x] XP tracking
- [x] Streak tracking
- [x] Skill progression
- [x] Profile API
- [x] Leaderboard API
- [x] Automated tests
- [x] CORS configuration

### Frontend

- [ ] Course / skill tree UI
- [ ] Lesson UI
- [ ] Exercise interactions
- [ ] Progress display
- [ ] Profile UI
- [ ] Leaderboard UI
- [ ] Backend integration

---

## Development Notes

The backend is intentionally kept simple and focused on the assignment requirements.

The application currently uses a seeded demo user rather than a full authentication system.

The SQLite database is suitable for local development and demonstration.

The frontend and backend communicate through REST APIs.

FastAPI automatically provides interactive API documentation through `/docs`.