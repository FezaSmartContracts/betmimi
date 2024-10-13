from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import UnauthorizedException
from ...core.schemas import Token
from ...models.user import UserRead
from ...core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
)

router = APIRouter(tags=["connect_wallet"])

@router.post("/user/connect", response_model=Token, status_code=201)
async def connect_user_wallet(
    response: Response, 
    user: UserRead, 
    db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict:
    """
    Connect a wallet to the application.
    - If the user is connecting their wallet for the first time, they are added to the database.
    - If the wallet is already connected, a session is established without creating a new user record.
    
    Args:
        response (Response): The response object.
        user (UserCreate): The user data containing the public address of the wallet.
        db (AsyncSession): The database session.
    
    Returns:
        dict: The user's information along with a session token.
    """
    db_user = await authenticate_user(public_address=user.public_address, db=db)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": db_user["public_address"]}, 
        expires_delta=access_token_expires
    )

    # Generate refresh token and set it as a secure HTTP-only cookie
    refresh_token = await create_refresh_token(data={"sub": db_user["public_address"]})
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token, 
        httponly=True, 
        secure=True, 
        samesite="Lax", 
        max_age=max_age
    )

    return {"access_token": access_token, "token_type": "bearer"}



@router.post("/refresh")
async def refresh_access_token(request: Request, db: AsyncSession = Depends(async_get_db)) -> dict[str, str]:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedException("Refresh token is missing or has expired.")

    user_data = await verify_token(refresh_token, db)
    if not user_data:
        raise UnauthorizedException("Refresh token is invalid or has been blacklisted.")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = await create_access_token(
        data={"sub": user_data.public_address},
        expires_delta=access_token_expires
    )

    return {"access_token": new_access_token, "token_type": "bearer"}