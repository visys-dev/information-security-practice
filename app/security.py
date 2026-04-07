import bcrypt


def hash_password(password: str) -> str:
    """
    Хешує пароль за допомогою bcrypt.
    Автоматично генерує унікальну сіль.

    Args:
    password: Пароль у відкритому вигляді
    Returns:
    bcrypt-хеш у форматі $2b$...
    """
    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Перевіряє пароль проти збереженого хешу.

    Args:
    plain_password: Пароль, введений користувачем
    hashed_password: Хеш з бази даних
    Returns:
    True якщо пароль правильний, False інакше
    """
    plain_password_bytes = plain_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
