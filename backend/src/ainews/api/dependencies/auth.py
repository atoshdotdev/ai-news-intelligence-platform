from typing import Annotated

from ainews.core.auth.security import decode_access_token
from ainews.core.db.database import get_session
from ainews.core.db.models import User
from ainews.core.repositories.user_repository import UserRepository
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session=Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_data = decode_access_token(token)
    except ValueError:
        raise credentials_exception

    user_repository = UserRepository(session)

    user = await user_repository.get_by_id(token_data.sub)

    if user is None:
        raise credentials_exception

    return user
