from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
    Table,
    Text,
)
from sqlalchemy.orm import relationship
from app.database import Base

# --- M:N таблиці ---

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)

# --- Моделі ---


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)

    roles = relationship("Role", secondary=user_roles, back_populates="users")
    group = relationship("Group", back_populates="students")
    grades = relationship(
        "Grade", back_populates="student", foreign_keys="Grade.student_id"
    )

    def __repr__(self):
        return f"<User {self.username}>"


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship(
        "Permission", secondary=role_permissions, back_populates="roles"
    )

    def __repr__(self):
        return f"<Role {self.name}>"


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    roles = relationship(
        "Role", secondary=role_permissions, back_populates="permissions"
    )

    def __repr__(self):
        return f"<Permission {self.name}>"


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False)
    department = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)

    students = relationship("User", back_populates="group")

    def __repr__(self):
        return f"<Group {self.name}>"


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    credits = Column(Float, nullable=False)
    semester = Column(Integer, nullable=False)

    grades = relationship("Grade", back_populates="subject")

    def __repr__(self):
        return f"<Subject {self.name}>"


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    grade = Column(Integer, nullable=False)
    date_assigned = Column(DateTime, default=datetime.utcnow)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    student = relationship("User", back_populates="grades", foreign_keys=[student_id])
    subject = relationship("Subject", back_populates="grades")
    teacher = relationship("User", foreign_keys=[assigned_by])

    def __repr__(self):
        return (
            f"<Grade student={self.student_id} "
            f"subject={self.subject_id} "
            f"grade={self.grade}>"
        )
