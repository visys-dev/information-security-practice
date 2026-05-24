from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):
    """Security audit table. Stores significant events using the 5W model."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # WHO
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)

    # WHAT
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    resource: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # WHEN
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # WHERE
    http_method: Mapped[str | None] = mapped_column(String(10), nullable=True)
    endpoint: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # WHY
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_audit_action_ts", "action", "timestamp"),
        Index("ix_audit_user_ts", "user_id", "timestamp"),
        Index("ix_audit_ip_action", "ip_address", "action"),
    )

