from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from web3.auto import w3

from ...core.config import settings
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import UnauthorizedException
from ...core.schemas import Token
from ...crud.crud_users import crud_users
from ...core.address_verification import verify_signature, generate_random
from ...schemas.users import (
    UserNonce,
    SignatureVerificationRequest,
    UserCreate,
    UserPublicAddress,
    UserReadNonce,
    UserUpdateInternal
)
from ...core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    verify_token,
)

router = APIRouter(tags=["connect_wallet"])

@router.post("/auth/nonce", response_model=UserNonce)
async def fetch_user_nonce(
    request: Request,
    user_address: UserPublicAddress,
    db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict:
    
    """
    - Primarily meant for fethcing user nonce. However, it creates a user and his balance if they don't exist
    - Eventually returns user `nonce`
    """
    
    address = user_address.public_address
    if not w3.is_address(address):
        raise HTTPException(status_code=400, detail="Invalid Ethereum address")
    
    public_address = address.lower()
    _nonce = generate_random()

    wallet: UserNonce | None = await crud_users.get(
        db=db, schema_to_select=UserNonce, public_address=public_address
    )

    if wallet is None:
        
        new_user_nonce: UserNonce = await crud_users.create(
            db,
            UserCreate(public_address=public_address, nonce=_nonce)
        )
        return new_user_nonce
    
    return wallet



@router.post("/user/connect", response_model=Token, status_code=201)
async def connect_user_wallet(
    request: Request,
    response: Response,
    user_data: SignatureVerificationRequest,
    db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict:
    """
    - Connect a wallet to the application.
        - If the wallet is verified, a session is established.
    Args:
       - `request (Request)`: The incoming request object.
       - `response (Response)`: The response object.
       - `user_data (SignatureVerificationRequest)`: The user data containing the public address and signature.
       - `db (AsyncSession)`: The database session.
    
    Returns:
       - `dict`: The user's information along with a session token.
    """
    fetched_user: UserReadNonce = await crud_users.get(
        db=db, schema_to_select=UserReadNonce, public_address=user_data.public_address.lower()
    )
    
    # Ensure user exists
    if not fetched_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    nonce = fetched_user.nonce

    # Attempt to verify the signature
    try:
        verify_signature(
            nonce=nonce,
            signature=user_data.signature,
            public_address=user_data.public_address
        )
    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Signature verification failed")

    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": fetched_user.id}, 
        expires_delta=access_token_expires
    )

    # Generate refresh token and set it as a secure HTTP-only cookie
    refresh_token = await create_refresh_token(data={"sub": fetched_user.id})
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token, 
        httponly=True, 
        secure=True, 
        samesite="Lax", 
        max_age=max_age
    )

    # Update the nonce after successful connection
    new_nonce = generate_random()
    await crud_users.update(
        db, 
        UserUpdateInternal(
            nonce=new_nonce
            ),
            id=fetched_user.id, 
            public_address=fetched_user.public_address
        )

    return {"access_token": access_token, "token_type": "bearer"}



@router.post("/refresh")
async def refresh_access_token(request: Request, db: AsyncSession = Depends(async_get_db)) -> dict[str, str]:
    """
    - called by frontend
    - refreshes access token
    """
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