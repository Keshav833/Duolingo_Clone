"""
Database connection setup.

SQLite + SQLAlchemy notes (since this is new to you):
- `engine` is the actual connection to the .db file. One per app.
- `SessionLocal` is a factory that makes a new DB "conversation" (Session)
  per request. You never share one session across requests.
- `check_same_thread=False` is SQLite-specific: by default SQLite refuses to
  let a connection be used by a different thread than the one that created
  it. FastAPI can handle a request in a different thread, so we disable that
  check. This is safe for our use case (single dev/small deployment).
- `Base` is the class every model (table) will inherit from. SQLAlchemy uses
  it to know which classes = which tables.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./duolingo.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency. Yields a DB session for the duration of one request,
    then closes it — even if the request raised an error.

    Usage in a route:
        @app.get("/skills")
        def list_skills(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()