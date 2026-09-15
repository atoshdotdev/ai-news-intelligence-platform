from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from ainews.core.config.settings import settings
from ainews.core.schemas.auth_schemas import TokenData
from ainews.core.utils.logger import logger


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    )

    return hashed.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(
    data: TokenData,
    expires_delta: timedelta | None = None,
) -> str:
    payload = data.model_dump()

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )

    payload["exp"] = expire

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        return TokenData(**payload)

    except jwt.ExpiredSignatureError as exc:
        logger.warning("Access token has expired")
        raise ValueError("Token has expired") from exc

    except jwt.InvalidTokenError as exc:
        logger.warning("Invalid access token")
        raise ValueError("Invalid token") from exc
