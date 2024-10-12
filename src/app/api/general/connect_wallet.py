from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Response
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from ...core.config import settings
from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import UnauthorizedException
from ...core.schemas import Token
from ...core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from ...core.security import blacklist_token, oauth2_scheme
from ...crud.crud_rate_limit import crud_rate_limits
from ...crud.crud_users import crud_users
from ...models.user import UserCreate, UserRead, UserEmailUpdate
from ...core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
)

router = APIRouter(tags=["connect_wallet"])

@router.post("/user/connect", response_model=UserRead, status_code=201)
async def connect_user_wallet(
    response: Response, user: UserCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict:
    """
    Connect a wallet to the application.
    - If the user is connecting their wallet for the first time, they are added to the database.
    - If the wallet is already connected, a session is established without creating a new user record.
    
    Args:
        request (Request): The request object.
        user (UserCreate): The user data containing the public address of the wallet.
        db (AsyncSession): The database session.
    
    Returns:
        dict: The user's information along with a session token.
    """
    db_user = await crud_users.exists(db=db, public_address=user.public_address)
    
    if not db_user:
        created_user = await crud_users.create(db=db, object=user)
        user_data = UserRead(id=created_user.id, public_address=created_user.public_address)
    else:
        user_data = UserRead(id=db_user["id"], public_address=db_user["public_address"])
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user_data.public_address}, expires_delta=access_token_expires)

    refresh_token = await create_refresh_token(data={"sub": user["username"]})
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    
    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="Lax", max_age=max_age
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh_access_token(request: Request, db: AsyncSession = Depends(async_get_db)) -> dict[str, str]:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedException("Refresh token missing.")

    user_data = await verify_token(refresh_token, db)
    if not user_data:
        raise UnauthorizedException("Invalid refresh token.")

    new_access_token = await create_access_token(data={"sub": user_data.username_or_email})
    return {"access_token": new_access_token, "token_type": "bearer"}
