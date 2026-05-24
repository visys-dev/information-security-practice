import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.audit.detector import get_security_stats
from app.audit.models import AuditLog
from app.auth.dependencies import require_role
from app.database import get_db
from app.models import User


router = APIRouter()


def _decode_details(details: str | None):
    if not details:
        return None
    try:
        return json.loads(details)
    except json.JSONDecodeError:
        return details


@router.get("/audit-log")
def get_audit_log(
    action: str | None = Query(default=None),
    username: str | None = Query(default=None),
    status: str | None = Query(default=None),
    hours: int = Query(24, ge=1, le=720),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Return filtered audit logs for administrators."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = db.query(AuditLog).filter(AuditLog.timestamp >= since)

    if action:
        query = query.filter(AuditLog.action == action)
    if username:
        query = query.filter(AuditLog.username == username)
    if status:
        query = query.filter(AuditLog.status == status)

    total = query.count()
    logs = (
        query.order_by(AuditLog.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "action": log.action,
                "status": log.status,
                "user_id": log.user_id,
                "username": log.username,
                "ip_address": log.ip_address,
                "http_method": log.http_method,
                "endpoint": log.endpoint,
                "status_code": log.status_code,
                "resource": log.resource,
                "details": _decode_details(log.details),
            }
            for log in logs
        ],
    }


@router.get("/security-stats")
def security_statistics(
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Return security statistics for administrators."""
    return get_security_stats(db, hours)

