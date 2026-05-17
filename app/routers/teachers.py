from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database import get_db
from app.models import Grade, User

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.get("/students/{student_id}/grades")
def get_student_grades(
    student_id: int,
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
):
    grades = db.query(Grade).filter(Grade.student_id == student_id).all()
    return {
        "student_id": student_id,
        "grades": [
            {
                "subject_id": grade.subject_id,
                "value": grade.grade,
                "date": grade.date_assigned.isoformat(),
            }
            for grade in grades
        ],
    }
