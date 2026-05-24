import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.audit.models import AuditLog


logger = logging.getLogger("security_audit")
logger.propagate = False

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            '{"timestamp":"%(asctime)s","level":"%(levelname)s","message":%(message)s}'
        )
    )
    logger.addHandler(handler)

logger.setLevel(logging.INFO)


def log_event(
    db: Session,
    action: str,
    status: str,
    ip_address: str,
    user_id: int | None = None,
    username: str | None = None,
    http_method: str | None = None,
    endpoint: str | None = None,
    status_code: int | None = None,
    resource: str | None = None,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    """Write a security event to the database and structured stdout logs."""
    log_entry = AuditLog(
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        action=action,
        resource=resource,
        timestamp=datetime.now(timezone.utc),
        http_method=http_method,
        endpoint=endpoint,
        status_code=status_code,
        status=status,
        details=json.dumps(details, ensure_ascii=False) if details else None,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    log_data = {
        "event_type": action,
        "status": status,
        "user_id": user_id,
        "username": username,
        "ip_address": ip_address,
        "endpoint": endpoint,
        "status_code": status_code,
    }
    if details:
        log_data["details"] = details

    level = logging.WARNING if status in {"failure", "warning", "error"} else logging.INFO
    logger.log(level, json.dumps(log_data, ensure_ascii=False))
    return log_entry


def log_login_success(db: Session, user_id: int, username: str, ip: str) -> AuditLog:
    return log_event(
        db=db,
        action="login_success",
        status="success",
        user_id=user_id,
        username=username,
        ip_address=ip,
        http_method="POST",
        endpoint="/auth/login",
        status_code=200,
    )


def log_login_failed(
    db: Session,
    username: str | None,
    ip: str,
    reason: str = "invalid_credentials",
    status_code: int = 401,
) -> AuditLog:
    return log_event(
        db=db,
        action="login_failed",
        status="failure",
        username=username,
        ip_address=ip,
        http_method="POST",
        endpoint="/auth/login",
        status_code=status_code,
        details={"reason": reason},
    )


def log_access_denied(
    db: Session,
    user_id: int | None,
    username: str | None,
    ip: str,
    endpoint: str,
) -> AuditLog:
    return log_event(
        db=db,
        action="access_denied",
        status="failure",
        user_id=user_id,
        username=username,
        ip_address=ip,
        endpoint=endpoint,
        status_code=403,
    )


def log_grade_change(
    db: Session,
    user_id: int,
    username: str,
    ip: str,
    student_id: int,
    subject: str,
    old_grade: int,
    new_grade: int,
) -> AuditLog:
    return log_event(
        db=db,
        action="grade_update",
        status="success",
        user_id=user_id,
        username=username,
        ip_address=ip,
        http_method="PUT",
        endpoint=f"/grades/{student_id}",
        status_code=200,
        resource=f"grades.student_id={student_id}",
        details={
            "student_id": student_id,
            "subject": subject,
            "old_grade": old_grade,
            "new_grade": new_grade,
        },
    )

