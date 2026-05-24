import sys
from pathlib import Path

from sqlalchemy import inspect, text

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.crypto.encryption import encrypt_field, field_lookup_hash
from app.database import SessionLocal


def _ensure_column(db, table_name: str, column_name: str, column_type: str) -> None:
    columns = {column["name"] for column in inspect(db.bind).get_columns(table_name)}
    if column_name not in columns:
        db.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))


def _ensure_unique_index(db, table_name: str, index_name: str, column_name: str) -> None:
    indexes = {index["name"] for index in inspect(db.bind).get_indexes(table_name)}
    if index_name not in indexes:
        db.execute(
            text(
                f"CREATE UNIQUE INDEX {index_name} "
                f"ON {table_name} ({column_name})"
            )
        )


def migrate() -> None:
    db = SessionLocal()
    try:
        _ensure_column(db, "users", "encrypted_email", "VARCHAR(255)")
        _ensure_column(db, "users", "email_hash", "VARCHAR(64)")
        _ensure_column(db, "users", "encrypted_phone", "VARCHAR(255)")

        columns = {column["name"] for column in inspect(db.bind).get_columns("users")}
        source_email = "email" if "email" in columns else "encrypted_email"

        users = db.execute(
            text(
                f"""
                SELECT id, {source_email}, encrypted_email
                FROM users
                WHERE encrypted_email IS NULL OR email_hash IS NULL
                """
            )
        ).fetchall()
        print(f"Found {len(users)} user records to migrate")

        for user_id, email, encrypted_email in users:
            if not email:
                continue
            value_to_encrypt = encrypted_email or email
            if isinstance(value_to_encrypt, str) and value_to_encrypt.startswith("gAAAA"):
                encrypted = value_to_encrypt
            else:
                encrypted = encrypt_field(str(value_to_encrypt).lower())

            db.execute(
                text(
                    """
                    UPDATE users
                    SET encrypted_email = :encrypted_email,
                        email_hash = :email_hash
                    WHERE id = :user_id
                    """
                ),
                {
                    "encrypted_email": encrypted,
                    "email_hash": field_lookup_hash(str(email).lower()),
                    "user_id": user_id,
                },
            )
            print(f"  User #{user_id}: email encrypted")

        db.commit()
        _ensure_unique_index(db, "users", "ix_users_email_hash", "email_hash")
        db.commit()
        print(f"Migration finished: {len(users)} records processed")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
