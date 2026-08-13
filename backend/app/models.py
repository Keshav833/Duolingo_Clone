"""
SQLAlchemy models — the full schema.

Course -> Unit -> Skill -> Lesson -> Exercise   (static content, seeded once)
User -> UserStats / UserSkillProgress / UserLessonProgress   (per-user state)

Read this top to bottom once; the pattern repeats for every table:
  1. __tablename__            -> actual table name in SQLite
  2. Column(...) attributes   -> the table's columns
  3. relationship(...)        -> not a real column. It's SQLAlchemy's way of
                                 letting you do `skill.lessons` in Python and
                                 get a list of Lesson objects, instead of you
                                 writing the JOIN yourself every time.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SAEnum,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


# ---------- enums ----------
# Python enums give you autocomplete + validation instead of magic strings
# scattered through the codebase. SQLAlchemy stores them as TEXT in SQLite.

class SkillStatus(str, enum.Enum):
    locked = "locked"
    available = "available"
    completed = "completed"


class ExerciseType(str, enum.Enum):
    multiple_choice = "multiple_choice"
    translate = "translate"          # word-bank translation
    match_pairs = "match_pairs"
    fill_blank = "fill_blank"
    type_answer = "type_answer"


# ---------- static content: Course -> Unit -> Skill -> Lesson -> Exercise ----------

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)          # e.g. "Spanish for English speakers"
    language = Column(String, nullable=False)       # e.g. "Spanish"
    slug = Column(String, unique=True, nullable=False)

    units = relationship(
        "Unit", back_populates="course", order_by="Unit.order", cascade="all, delete-orphan"
    )


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    order = Column(Integer, nullable=False)          # position in the course

    course = relationship("Course", back_populates="units")
    skills = relationship(
        "Skill", back_populates="unit", order_by="Skill.order", cascade="all, delete-orphan"
    )


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    title = Column(String, nullable=False)            # e.g. "Basics 1"
    icon = Column(String, nullable=True)               # icon name/emoji for the tree node
    order = Column(Integer, nullable=False)

    unit = relationship("Unit", back_populates="skills")
    lessons = relationship(
        "Lesson", back_populates="skill", order_by="Lesson.order", cascade="all, delete-orphan"
    )


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    order = Column(Integer, nullable=False)             # lesson N within the skill
    xp_reward = Column(Integer, default=10, nullable=False)

    skill = relationship("Skill", back_populates="lessons")
    exercises = relationship(
        "Exercise", back_populates="lesson", order_by="Exercise.order", cascade="all, delete-orphan"
    )


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    order = Column(Integer, nullable=False)
    type = Column(SAEnum(ExerciseType), nullable=False)

    question = Column(String, nullable=False)
    # JSON keeps one table working for all 5 exercise types instead of 5 tables.
    # multiple_choice: {"choices": ["a","b","c"], "correct": "b"}
    # translate:       {"word_bank": ["I","eat","apple"], "correct": ["I","eat","an","apple"]}
    # match_pairs:     {"pairs": [["hola","hello"], ["gato","cat"]]}
    # fill_blank:      {"sentence": "Yo ___ manzanas", "correct": "como"}
    # type_answer:     {"correct": "gato"}
    options = Column(JSON, nullable=True)
    correct_answer = Column(JSON, nullable=False)

    lesson = relationship("Lesson", back_populates="exercises")


# ---------- users & per-user state ----------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    # No real auth required by the spec — this is a placeholder hook so a
    # login screen can be bolted on later without touching the schema.
    created_at = Column(DateTime, default=datetime.utcnow)

    stats = relationship(
        "UserStats", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    skill_progress = relationship("UserSkillProgress", back_populates="user", cascade="all, delete-orphan")
    lesson_progress = relationship("UserLessonProgress", back_populates="user", cascade="all, delete-orphan")


class UserStats(Base):
    """One row per user. The numbers driving the top bar of the UI."""
    __tablename__ = "user_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    xp_total = Column(Integer, default=0, nullable=False)
    streak_count = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(DateTime, nullable=True)   # used to compute streak continuation

    hearts = Column(Integer, default=5, nullable=False)
    hearts_max = Column(Integer, default=5, nullable=False)
    last_heart_lost_at = Column(DateTime, nullable=True)    # used for heart regen timer

    # gems intentionally not persisted — spec allows mocking currency in the
    # UI only (💎 500, static), no earn/spend logic required.
    daily_xp_goal = Column(Integer, default=30, nullable=False)
    daily_xp_earned = Column(Integer, default=0, nullable=False)  # resets when day rolls over

    user = relationship("User", back_populates="stats")


class UserSkillProgress(Base):
    """One row per (user, skill). Drives locked/unlocked/completed + crown level on the tree."""
    __tablename__ = "user_skill_progress"
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)

    status = Column(SAEnum(SkillStatus), default=SkillStatus.locked, nullable=False)  # first skill seeded as .available
    crowns = Column(Integer, default=0, nullable=False)          # progress level within a skill
    lessons_completed = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="skill_progress")
    skill = relationship("Skill")


class UserLessonProgress(Base):
    """One row per (user, lesson) attempt/completion. Feeds skill progress + XP history."""
    __tablename__ = "user_lesson_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)

    completed = Column(Boolean, default=False, nullable=False)
    xp_earned = Column(Integer, default=0, nullable=False)
    accuracy = Column(Float, nullable=True)          # % correct on first try, for stats/profile
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="lesson_progress")
    lesson = relationship("Lesson")