from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Grade, User

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/me/grades")
def get_my_grades(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    grades = db.query(Grade).filter(Grade.student_id == current_user.id).all()
    return {
        "student": current_user.username,
        "grades": [
            {
                "subject_id": grade.subject_id,
                "value": grade.grade,
                "date": grade.date_assigned.isoformat(),
            }
            for grade in grades
        ],
    }
