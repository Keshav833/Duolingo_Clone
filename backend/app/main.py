"""
FastAPI app entrypoint.

Equivalent of your Express `app.js`/`server.js`: creates the app instance,
sets up middleware (CORS), and mounts routers. Run with:
    uvicorn app.main:app --reload
from inside backend/, with the venv active.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routes import user as user_routes
from .routes import course as course_routes
from .routes import lessons as lessons_routes
from .routes import answer as answer_routes
from .routes import complete as complete_routes
from .routes import skills as skills_routes
from .routes import profile as profile_routes
from .routes import leaderboard as leaderboard_routes

# Ensures tables exist on startup. Unlike seed.py, this does NOT drop
# existing data — create_all() only creates tables that don't already
# exist, so it's safe to run every time the server starts.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Duolingo Clone API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://duolingo-clone-ma82.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router)
app.include_router(course_routes.router)
app.include_router(lessons_routes.router)
app.include_router(answer_routes.router)
app.include_router(complete_routes.router)
app.include_router(skills_routes.router)
app.include_router(profile_routes.router)
app.include_router(leaderboard_routes.router)

@app.get("/")
def root():
    return {"status": "ok", "service": "duolingo-clone-api"}