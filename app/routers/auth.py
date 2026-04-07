from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, LoginRequest, LoginResponse
from app.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Реєстрація нового користувача",
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Реєстрація користувача
    """

    # Нормалізація email
    email = user_data.email.lower()

    # Перевірка username
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username вже існує",
        )

    # Перевірка email
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email вже зареєстровано",
        )

    # Створення користувача
    new_user = User(
        username=user_data.username,
        email=email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Помилка збереження користувача",
        )

    return new_user


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Вхід користувача",
)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Аутентифікація користувача
    """

    # Пошук користувача + підвантаження ролей
    user = (
        db.query(User)
        .options(joinedload(User.roles))
        .filter(User.username == credentials.username)
        .first()
    )

    # Захист від enumeration attack
    try:
        is_valid_password = bool(
            user and verify_password(credentials.password, user.password_hash)
        )
    except ValueError:
        is_valid_password = False

    if not is_valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний логін або пароль",
        )

    # Перевірка активності
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Акаунт деактивовано",
        )

    # Отримання ролей
    user_roles = [role.name for role in user.roles]

    return LoginResponse(
        message="Вхід успішний",
        user_id=user.id,
        username=user.username,
        roles=user_roles,
    )
