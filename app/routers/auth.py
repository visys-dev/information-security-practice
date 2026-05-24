from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from jose import JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.auth.dependencies import get_current_user
from app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.crypto.encryption import field_lookup_hash
from app.database import get_db
from app.middleware.rate_limiter import limiter
from app.models import User
from app.schemas import (
    LoginRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserCreate,
    UserInfo,
    UserResponse,
)
from app.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Реєстрація нового користувача",
)
@limiter.limit("10/minute")
def register(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
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
    if db.query(User).filter(User.email_hash == field_lookup_hash(email)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email вже зареєстровано",
        )

    # Створення користувача
    new_user = User(
        username=user_data.username,
        email=email,
        phone=user_data.phone,
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
    response_model=TokenResponse,
    summary="Вхід користувача",
)
@limiter.limit("5/minute")
def login(
    request: Request,
    credentials: LoginRequest | None = Body(default=None),
    username: str | None = Query(
        default=None,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
    ),
    password: str | None = Query(default=None, min_length=1, max_length=128),
    db: Session = Depends(get_db),
):
    """
    Аутентифікація користувача та видача JWT access/refresh токенів.
    """
    if credentials is not None:
        username = credentials.username
        password = credentials.password
    elif username is not None and password is not None:
        try:
            credentials = LoginRequest(username=username, password=password)
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=exc.errors(),
            )
        username = credentials.username
        password = credentials.password

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Передайте username і password у JSON body або query params",
        )

    # Пошук користувача + підвантаження ролей
    user = (
        db.query(User)
        .options(joinedload(User.roles))
        .filter(User.username == username)
        .first()
    )

    # Захист від enumeration attack
    try:
        is_valid_password = bool(user and verify_password(password, user.password_hash))
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

    role = user.roles[0].name if user.roles else "student"
    access_token = create_access_token(user.id, role)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Оновлення access token",
)
def refresh_token(body: TokenRefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = verify_token(body.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалідний refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Потрібен refresh token, а не access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token не містить коректного користувача",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = (
        db.query(User)
        .options(joinedload(User.roles))
        .filter(User.id == user_id)
        .first()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача не знайдено",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Акаунт деактивовано",
        )

    role = user.roles[0].name if user.roles else "student"
    return TokenResponse(
        access_token=create_access_token(user.id, role),
        refresh_token=create_refresh_token(user.id),
    )


@router.get(
    "/me",
    response_model=UserInfo,
    summary="Поточний автентифікований користувач",
)
def get_me(current_user: User = Depends(get_current_user)):
    role = current_user.roles[0].name if current_user.roles else "student"
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        phone=current_user.phone,
        full_name=current_user.full_name,
        role=role,
    )
