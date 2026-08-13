"""
Shared FastAPI dependencies.

The assignment explicitly allows skipping real auth and assuming a single
logged-in learner. Instead of hardcoding CURRENT_USER_ID = 1 in every route,
we centralize "who is the current user" in one function. When/if real auth
gets added later, this is the only place that changes — every route that
depends on get_current_user keeps working unmodified.
"""

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from . import models

CURRENT_USERNAME = "Keshav"  # matches the username seeded in seed.py


def get_current_user(db: Session = Depends(get_db)) -> models.User:
    user = db.query(models.User).filter(models.User.username == CURRENT_USERNAME).first()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail=f"Seeded user '{CURRENT_USERNAME}' not found. Run `python -m app.seed` first.",
        )
    return user