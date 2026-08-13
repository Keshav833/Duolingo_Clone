"""
Course route — powers the learning path / skill tree screen.

The core job here is a merge, not a query: Skill (static content) and
UserSkillProgress (per-user state) are separate tables by design (see
models.py), so this route is where they get combined into the single
shape the frontend actually wants to render.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..dependencies import get_current_user
from ..schemas.course import CourseOut, UnitOut, SkillOut

router = APIRouter(prefix="/api", tags=["course"])


@router.get("/course", response_model=CourseOut)
def get_course(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Single seeded course for this assignment — .first() is fine here.
    # (Relationship order_by on Unit.order / Skill.order, defined in
    # models.py, means course.units and unit.skills come back pre-sorted —
    # no manual sorting needed here.)
    course = db.query(models.Course).first()
    if course is None:
        raise HTTPException(status_code=404, detail="No course found. Run `python -m app.seed` first.")

    # Build a skill_id -> progress lookup once, instead of querying
    # UserSkillProgress once per skill inside the loop below.
    progress_by_skill = {p.skill_id: p for p in current_user.skill_progress}

    units_out = []
    for unit in course.units:
        skills_out = []
        for skill in unit.skills:
            progress = progress_by_skill.get(skill.id)
            # Defensive default: a skill with no progress row yet (e.g. a
            # newly added skill the seed/migration hasn't caught up to)
            # is simply locked, not a crash.
            skills_out.append(
                SkillOut(
                    id=skill.id,
                    title=skill.title,
                    icon=skill.icon,
                    order=skill.order,
                    status=progress.status if progress else models.SkillStatus.locked,
                    crowns=progress.crowns if progress else 0,
                    lessons_completed=progress.lessons_completed if progress else 0,
                )
            )
        units_out.append(
            UnitOut(id=unit.id, title=unit.title, order=unit.order, skills=skills_out)
        )

    return CourseOut(id=course.id, name=course.name, language=course.language, units=units_out)