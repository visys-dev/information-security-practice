import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from cryptography.fernet import Fernet

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.crypto.key_manager import get_encryption_key


def create_backup() -> str:
    db_path = Path(os.getenv("DATABASE_FILE", "data/app.db"))
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("data/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir / f"{db_path.stem}_backup_{timestamp}.db"
    shutil.copy2(db_path, backup_path)

    fernet = Fernet(get_encryption_key())
    encrypted_path = backup_path.with_suffix(".db.enc")
    encrypted_path.write_bytes(fernet.encrypt(backup_path.read_bytes()))
    backup_path.unlink()

    print(f"Encrypted backup created: {encrypted_path}")
    return str(encrypted_path)


if __name__ == "__main__":
    create_backup()
