import hashlib
import hmac

from cryptography.fernet import Fernet, InvalidToken

from app.crypto.key_manager import get_encryption_key


DECRYPTION_ERROR = "[ПОМИЛКА РОЗШИФРУВАННЯ - невірний ключ]"


def get_fernet() -> Fernet:
    """Create a Fernet instance with the current application key."""
    return Fernet(get_encryption_key())


def encrypt_field(value: str | None) -> str | None:
    """Encrypt a string value for storage in the database."""
    if value is None or value == "":
        return value

    encrypted = get_fernet().encrypt(value.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_field(encrypted_value: str | None) -> str | None:
    """Decrypt a database value, returning a clear error marker on key mismatch."""
    if encrypted_value is None or encrypted_value == "":
        return encrypted_value

    try:
        decrypted = get_fernet().decrypt(encrypted_value.encode("utf-8"))
    except (InvalidToken, ValueError):
        return DECRYPTION_ERROR
    return decrypted.decode("utf-8")


def field_lookup_hash(value: str | None) -> str | None:
    """
    Create a deterministic keyed hash for equality checks on encrypted fields.

    Fernet ciphertext changes on every write, so unique constraints and duplicate
    checks need a separate non-reversible lookup value.
    """
    if value is None or value == "":
        return None

    normalized = value.strip().lower().encode("utf-8")
    return hmac.new(get_encryption_key(), normalized, hashlib.sha256).hexdigest()

