from ainews.core.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from ainews.core.db.models import User
from ainews.core.repositories.user_repository import UserRepository
from ainews.core.schemas.auth_schemas import (
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

    async def register(self, request: RegisterRequest) -> UserRead:
        existing_user = await self.user_repository.get_by_username(request.username)

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists",
            )

        user = User(
            username=request.username,
            hashed_password=hash_password(request.password),
            name=request.name,
        )

        user = await self.user_repository.create(user)

        return UserRead.model_validate(user)

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
