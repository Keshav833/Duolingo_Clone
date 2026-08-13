"""
Seed script — wipes and repopulates the database with demo content.

Run with:
    python -m app.seed

Safe to run repeatedly: every run drops all tables and recreates them from
scratch (Base.metadata.drop_all + create_all), so you never get duplicate
rows from running it twice. This is a dev-time reset, not an incremental
"insert if missing" — fine for us since there's no real user data to protect.

Content shape:
    Course: Spanish for Beginners
      Unit 1: Basics
        Skill: Greetings      -> 2 lessons
        Skill: Introductions  -> 2 lessons
      Unit 2: Everyday Words
        Skill: Food           -> 2 lessons
        Skill: Family         -> 2 lessons
    8 lessons x 5 exercises (one of each type) = 40 exercises total.

JSON shape convention for Exercise.options / Exercise.correct_answer
(kept uniform across all 5 types so the frontend has one parsing pattern,
not five):
    multiple_choice : options={"choices": [...]}          correct_answer={"correct": "..."}
    translate       : options={"word_bank": [...]}        correct_answer={"correct": [...]}   (ordered)
    match_pairs     : options={"pairs": [[es,en], ...]}   correct_answer={es: en, ...}
    fill_blank      : options=None                        correct_answer={"correct": "..."}
    type_answer     : options=None                        correct_answer={"correct": "..."}
"""

from datetime import datetime, timedelta

from .database import Base, engine, SessionLocal
from . import models
from .models import (
    Course,
    Unit,
    Skill,
    Lesson,
    Exercise,
    ExerciseType,
    User,
    UserStats,
    UserSkillProgress,
    UserLessonProgress,
    SkillStatus,
)


def mc(question, choices, correct):
    """multiple_choice exercise dict"""
    return dict(
        type=ExerciseType.multiple_choice,
        question=question,
        options={"choices": choices},
        correct_answer={"correct": correct},
    )


def translate(question, word_bank, correct_sequence):
    """translate / word-bank exercise dict"""
    return dict(
        type=ExerciseType.translate,
        question=question,
        options={"word_bank": word_bank},
        correct_answer={"correct": correct_sequence},
    )


def match_pairs(question, pairs):
    """match_pairs exercise dict. pairs: list of [spanish, english]"""
    return dict(
        type=ExerciseType.match_pairs,
        question=question,
        options={"pairs": pairs},
        correct_answer={es: en for es, en in pairs},
    )


def fill_blank(sentence, correct):
    """fill_blank exercise dict. `sentence` should contain '___' for the blank."""
    return dict(
        type=ExerciseType.fill_blank,
        question=sentence,
        options=None,
        correct_answer={"correct": correct},
    )


def type_answer(question, correct):
    """type_answer exercise dict — free-text, no options."""
    return dict(
        type=ExerciseType.type_answer,
        question=question,
        options=None,
        correct_answer={"correct": correct},
    )


# ---------- course content ----------
# Each skill has 2 lessons; each lesson is a list of exactly 5 exercise dicts
# (one of each type), built with the helpers above.

COURSE = {
    "name": "Spanish for Beginners",
    "language": "Spanish",
    "slug": "spanish-beginners",
    "units": [
        {
            "title": "Basics",
            "skills": [
                {
                    "title": "Greetings",
                    "icon": "👋",
                    "lessons": [
                        [
                            mc("What does 'hola' mean?", ["Hello", "Goodbye", "Thanks", "Please"], "Hello"),
                            translate("Translate: 'Good morning'", ["Buenos", "días", "noches", "tardes"], ["Buenos", "días"]),
                            match_pairs("Match the greetings", [["hola", "hello"], ["adiós", "goodbye"], ["gracias", "thanks"]]),
                            fill_blank("___ días (Good morning)", "Buenos"),
                            type_answer("How do you say 'goodbye' in Spanish?", "adiós"),
                        ],
                        [
                            mc("What does 'buenas noches' mean?", ["Good night", "Good morning", "See you later", "Please"], "Good night"),
                            translate("Translate: 'See you later'", ["Hasta", "luego", "pronto", "mañana"], ["Hasta", "luego"]),
                            match_pairs("Match the phrases", [["buenas tardes", "good afternoon"], ["hasta luego", "see you later"], ["por favor", "please"]]),
                            fill_blank("Hasta ___ (see you later)", "luego"),
                            type_answer("How do you say 'please' in Spanish?", "por favor"),
                        ],
                    ],
                },
                {
                    "title": "Introductions",
                    "icon": "🤝",
                    "lessons": [
                        [
                            mc("What does 'me llamo' mean?", ["My name is", "I am from", "How are you", "Nice to meet you"], "My name is"),
                            translate("Translate: 'My name is Ana'", ["Me", "llamo", "Ana", "soy"], ["Me", "llamo", "Ana"]),
                            match_pairs("Match the introductions", [["me llamo", "my name is"], ["mucho gusto", "nice to meet you"], ["soy de", "I am from"]]),
                            fill_blank("Mucho ___ (nice to meet you)", "gusto"),
                            type_answer("How do you say 'nice to meet you' in Spanish?", "mucho gusto"),
                        ],
                        [
                            mc("What does '¿cómo estás?' mean?", ["How are you?", "What's your name?", "Where are you from?", "Goodbye"], "How are you?"),
                            translate("Translate: 'I am fine'", ["Estoy", "bien", "mal", "yo"], ["Estoy", "bien"]),
                            match_pairs("Match the responses", [["¿cómo estás?", "how are you?"], ["estoy bien", "I am fine"], ["¿y tú?", "and you?"]]),
                            fill_blank("Estoy ___ (I am fine)", "bien"),
                            type_answer("How do you ask 'how are you?' in Spanish?", "¿cómo estás?"),
                        ],
                    ],
                },
            ],
        },
        {
            "title": "Everyday Words",
            "skills": [
                {
                    "title": "Food",
                    "icon": "🍎",
                    "lessons": [
                        [
                            mc("What does 'manzana' mean?", ["Apple", "Bread", "Water", "Milk"], "Apple"),
                            translate("Translate: 'I eat bread'", ["Yo", "como", "pan", "bebo"], ["Yo", "como", "pan"]),
                            match_pairs("Match the food words", [["manzana", "apple"], ["pan", "bread"], ["agua", "water"]]),
                            fill_blank("Yo ___ manzanas (I eat apples)", "como"),
                            type_answer("How do you say 'water' in Spanish?", "agua"),
                        ],
                        [
                            mc("What does 'beber' mean?", ["To drink", "To eat", "To cook", "To buy"], "To drink"),
                            translate("Translate: 'I drink water'", ["Yo", "bebo", "agua", "como"], ["Yo", "bebo", "agua"]),
                            match_pairs("Match the food verbs/words", [["beber", "to drink"], ["comer", "to eat"], ["leche", "milk"]]),
                            fill_blank("Yo ___ agua (I drink water)", "bebo"),
                            type_answer("How do you say 'milk' in Spanish?", "leche"),
                        ],
                    ],
                },
                {
                    "title": "Family",
                    "icon": "👪",
                    "lessons": [
                        [
                            mc("What does 'madre' mean?", ["Mother", "Father", "Sister", "Brother"], "Mother"),
                            translate("Translate: 'My family'", ["Mi", "familia", "padre", "mi"], ["Mi", "familia"]),
                            match_pairs("Match the family words", [["madre", "mother"], ["padre", "father"], ["familia", "family"]]),
                            fill_blank("Mi ___ (my mother)", "madre"),
                            type_answer("How do you say 'father' in Spanish?", "padre"),
                        ],
                        [
                            mc("What does 'hermano' mean?", ["Brother", "Sister", "Cousin", "Uncle"], "Brother"),
                            translate("Translate: 'My sister'", ["Mi", "hermana", "hermano", "familia"], ["Mi", "hermana"]),
                            match_pairs("Match the sibling words", [["hermano", "brother"], ["hermana", "sister"], ["primo", "cousin"]]),
                            fill_blank("Mi ___ (my brother)", "hermano"),
                            type_answer("How do you say 'sister' in Spanish?", "hermana"),
                        ],
                    ],
                },
            ],
        },
    ],
}


def seed():
    print("Dropping and recreating all tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # ---------- content: Course -> Unit -> Skill -> Lesson -> Exercise ----------
        course = Course(name=COURSE["name"], language=COURSE["language"], slug=COURSE["slug"])
        db.add(course)
        db.flush()  # assigns course.id without committing yet

        skill_objs = []  # keep ordered list of created Skill rows for progress seeding below

        for unit_order, unit_data in enumerate(COURSE["units"], start=1):
            unit = Unit(course_id=course.id, title=unit_data["title"], order=unit_order)
            db.add(unit)
            db.flush()

            for skill_order, skill_data in enumerate(unit_data["skills"], start=1):
                skill = Skill(
                    unit_id=unit.id,
                    title=skill_data["title"],
                    icon=skill_data["icon"],
                    order=skill_order,
                )
                db.add(skill)
                db.flush()
                skill_objs.append(skill)

                for lesson_order, exercises in enumerate(skill_data["lessons"], start=1):
                    lesson = Lesson(skill_id=skill.id, order=lesson_order, xp_reward=10)
                    db.add(lesson)
                    db.flush()

                    for ex_order, ex_data in enumerate(exercises, start=1):
                        db.add(Exercise(lesson_id=lesson.id, order=ex_order, **ex_data))

        db.flush()

        # ---------- demo user ----------
        user = User(username="Keshav")
        db.add(user)
        db.flush()

        db.add(
            UserStats(
                user_id=user.id,
                xp_total=120,
                streak_count=3,
                last_activity_date=datetime.utcnow() - timedelta(hours=2),
                hearts=5,
                hearts_max=5,
                daily_xp_goal=30,
                daily_xp_earned=20,
            )
        )

        # skill_objs is in seed order: [Greetings, Introductions, Food, Family]
        greetings, introductions, food, family = skill_objs

        db.add(UserSkillProgress(user_id=user.id, skill_id=greetings.id, status=SkillStatus.completed, crowns=2, lessons_completed=2))
        db.add(UserSkillProgress(user_id=user.id, skill_id=introductions.id, status=SkillStatus.available, crowns=0, lessons_completed=0))
        db.add(UserSkillProgress(user_id=user.id, skill_id=food.id, status=SkillStatus.locked, crowns=0, lessons_completed=0))
        db.add(UserSkillProgress(user_id=user.id, skill_id=family.id, status=SkillStatus.locked, crowns=0, lessons_completed=0))

        # lesson progress rows for the 2 completed Greetings lessons
        for lesson in greetings.lessons:
            db.add(
                UserLessonProgress(
                    user_id=user.id,
                    lesson_id=lesson.id,
                    completed=True,
                    xp_earned=lesson.xp_reward,
                    accuracy=100.0,
                    completed_at=datetime.utcnow() - timedelta(hours=2),
                )
            )

        db.commit()

        exercise_count = db.query(Exercise).count()
        print(f"Seeded: 1 course, 2 units, 4 skills, 8 lessons, {exercise_count} exercises, 1 user.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()