from fastapi import APIRouter, HTTPException, status

from app.schemas import CommentCreate, CommentResponse
from app.validators.sanitizer import contains_sql_patterns

router = APIRouter(prefix="/demo", tags=["Security Demo"])


@router.post("/comment", response_model=CommentResponse)
def create_comment(comment: CommentCreate):
    if contains_sql_patterns(comment.text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SQL-патерни виявлені",
        )

    return CommentResponse(text=comment.text)
