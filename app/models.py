from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.crypto.encryption import decrypt_field, encrypt_field, field_lookup_hash
from app.database import Base

# --- M:N таблиці (ТУТ тільки Column!) ---

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
)

# --- Моделі ---


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    _encrypted_email: Mapped[str] = mapped_column(
        "encrypted_email", String(255), nullable=False
    )
    email_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    _encrypted_phone: Mapped[str | None] = mapped_column(
        "encrypted_phone", String(255), nullable=True
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"), nullable=True)

    # relationships
    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary=user_roles, back_populates="users"
    )
    group: Mapped["Group"] = relationship("Group", back_populates="students")
    grades: Mapped[list["Grade"]] = relationship(
        "Grade",
        back_populates="student",
        foreign_keys="Grade.student_id",
    )

    @property
    def email(self) -> str:
        return decrypt_field(self._encrypted_email) or ""

    @email.setter
    def email(self, value: str) -> None:
        normalized = value.strip().lower()
        self._encrypted_email = encrypt_field(normalized) or ""
        self.email_hash = field_lookup_hash(normalized) or ""

    @property
    def phone(self) -> str | None:
        return decrypt_field(self._encrypted_phone)

    @phone.setter
    def phone(self, value: str | None) -> None:
        self._encrypted_phone = encrypt_field(value.strip()) if value else None

    def __repr__(self):
        return f"<User {self.username}>"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    users: Mapped[list["User"]] = relationship(
        "User", secondary=user_roles, back_populates="roles"
    )
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission", secondary=role_permissions, back_populates="roles"
    )

    def __repr__(self):
        return f"<Role {self.name}>"


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary=role_permissions, back_populates="permissions"
    )

    def __repr__(self):
        return f"<Permission {self.name}>"


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column()

    students: Mapped[list["User"]] = relationship("User", back_populates="group")

    def __repr__(self):
        return f"<Group {self.name}>"


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    credits: Mapped[float] = mapped_column(Float, nullable=False)
    semester: Mapped[int] = mapped_column()

    grades: Mapped[list["Grade"]] = relationship("Grade", back_populates="subject")

    def __repr__(self):
        return f"<Subject {self.name}>"


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)

    grade: Mapped[int] = mapped_column()
    date_assigned: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    assigned_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # relationships
    student: Mapped["User"] = relationship(
        "User",
        back_populates="grades",
        foreign_keys=[student_id],
    )
    subject: Mapped["Subject"] = relationship("Subject", back_populates="grades")
    teacher: Mapped["User"] = relationship(
        "User",
        foreign_keys=[assigned_by],
    )

    def __repr__(self):
        return (
            f"<Grade student={self.student_id} "
            f"subject={self.subject_id} "
            f"grade={self.grade}>"
        )
