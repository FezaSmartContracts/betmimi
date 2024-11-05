from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.db.database import async_get_db
from ..core.exceptions.http_exceptions import ForbiddenException, RateLimitException, UnauthorizedException
from ..core.logger import logging
from ..core.security import verify_token
from ..core.utils.rate_limit import is_rate_limited
from ..crud.crud_rate_limit import crud_rate_limits
from ..crud.crud_users import crud_users
from ..models.user import User
from ..models.rate_limit import sanitize_path

logger = logging.getLogger(__name__)

DEFAULT_LIMIT = settings.DEFAULT_RATE_LIMIT_LIMIT
DEFAULT_PERIOD = settings.DEFAULT_RATE_LIMIT_PERIOD


async def get_current_user(
    token: Annotated[str, Header(alias="Authorization")], 
    db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any] | None:
    # Extract the actual token from the 'Bearer' authorization header
    if not token.startswith("Bearer "):
        raise UnauthorizedException("Invalid token format.")
    token_value = token.split(" ")[1]

    # Verify the token and retrieve token data
    token_data = await verify_token(token_value, db)
    if not token_data:
        raise UnauthorizedException("User not authenticated.")

    # Fetch the user based on public_address
    user = await crud_users.get(db=db, public_address=token_data.public_address.lower(), is_deleted=False)

    # Check if user is found and return user data
    if user:
        return user

    raise UnauthorizedException("User not authenticated.")


async def get_optional_user(request: Request, db: AsyncSession = Depends(async_get_db)) -> dict | None:
    token = request.headers.get("Authorization")
    if not token:
        return None

    try:
        token_type, _, token_value = token.partition(" ")
        if token_type.lower() != "bearer" or not token_value:
            return None

        token_data = await verify_token(token_value, db)
        if token_data is None:
            return None

        return await get_current_user(token_value, db=db)

    except HTTPException as http_exc:
        if http_exc.status_code != 401:
            logger.error(f"Unexpected HTTPException in get_optional_user: {http_exc.detail}")
        return None

    except Exception as exc:
        logger.error(f"Unexpected error in get_optional_user: {exc}")
        return None


async def get_current_superuser(current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    if not current_user["is_superuser"]:
        raise ForbiddenException("You do not have enough privileges.")

    return current_user

async def get_admin(current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    if not current_user["is_admin"]:
        raise ForbiddenException("You do not have enough privileges.")

    return current_user


async def rate_limiter(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], user: User | None = Depends(get_optional_user)
) -> None:
    path = sanitize_path(request.url.path)
    if user:
        user_id = user["id"]
        rate_limit = await crud_rate_limits.get(db=db, path=path)
        if rate_limit:
            limit, period = rate_limit["limit"], rate_limit["period"]
        else:
            logger.warning(
                f"User {user_id} has no specific rate limit for path '{path}'. \
                    Applying default rate limit."
            )
            limit, period = DEFAULT_LIMIT, DEFAULT_PERIOD
    else:
        user_id = request.client.host
        limit, period = DEFAULT_LIMIT, DEFAULT_PERIOD

    is_limited = await is_rate_limited(db=db, user_id=user_id, path=path, limit=limit, period=period)
    if is_limited:
        raise RateLimitException("Rate limit exceeded.")
