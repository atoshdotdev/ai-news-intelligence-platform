from ainews.core.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from ainews.core.db.models import User
from ainews.core.repositories.user_repository import UserRepository
from ainews.core.schemas.auth_schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    TokenData,
    TokenResponse,
    UserRead,
)
from fastapi import HTTPException, status


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register(self, data: RegisterRequest) -> AuthResponse:
        existing_user = await self.user_repository.get_by_username(data.username)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists",
            )

        user = User(
            username=data.username,
            hashed_password=hash_password(data.password),
            name=data.name,
        )

        user = await self.user_repository.create(user)

        access_token = create_access_token(TokenData(sub=str(user.id)))

        return AuthResponse(
            user=UserRead.model_validate(user),
            token=TokenResponse(access_token=access_token),
        )

    async def login(self, request: LoginRequest) -> TokenResponse:
        user = await self.user_repository.get_by_username(request.username)

        if user is None or not verify_password(
            request.password,
            user.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token(
            TokenData(sub=str(user.id)),
        )

        return TokenResponse(access_token=token)
