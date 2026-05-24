from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.audit.logger import log_event
from app.audit.models import AuditLog


def check_brute_force(
    db: Session,
    ip_address: str,
    threshold: int = 5,
    window_minutes: int = 5,
) -> bool:
    """Return True when failed logins from one IP exceed the threshold."""
    since = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    failed_count = (
        db.query(func.count(AuditLog.id))
        .filter(
            AuditLog.action == "login_failed",
            AuditLog.ip_address == ip_address,
            AuditLog.timestamp >= since,
        )
        .scalar()
    )

    if failed_count >= threshold:
        log_event(
            db=db,
            action="brute_force_detected",
            status="warning",
            ip_address=ip_address,
            details={
                "failed_attempts": failed_count,
                "window_minutes": window_minutes,
            },
        )
        return True
    return False


def check_off_hours_access(
    db: Session,
    user_id: int,
    username: str,
    ip: str,
    hour: int,
) -> bool:
    """Log a warning for logins between 00:00 and 06:00 UTC."""
    if 0 <= hour < 6:
        log_event(
            db=db,
            action="off_hours_login",
            status="warning",
            user_id=user_id,
            username=username,
            ip_address=ip,
            details={"login_hour": hour},
        )
        return True
    return False


def get_security_stats(db: Session, hours: int = 24) -> dict:
    """Return security KPI counters for the last N hours."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    def count_for(action: str | None = None) -> int:
        query = db.query(func.count(AuditLog.id)).filter(AuditLog.timestamp >= since)
        if action:
            query = query.filter(AuditLog.action == action)
        return int(query.scalar() or 0)

    return {
        "period_hours": hours,
        "total_events": count_for(),
        "failed_logins": count_for("login_failed"),
        "access_denied": count_for("access_denied"),
        "brute_force_alerts": count_for("brute_force_detected"),
        "grade_changes": count_for("grade_update"),
    }

