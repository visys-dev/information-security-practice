import os


def get_encryption_key() -> bytes:
    """Return the Fernet key from the environment."""
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise RuntimeError(
            "ENCRYPTION_KEY is not set. Generate one with: "
            "python scripts/generate_key.py"
        )
    return key.encode("utf-8")

