from datetime import timedelta
from typing import Annotated
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from web3.auto import w3

from ...core.config import settings
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import UnauthorizedException
from ...core.schemas import Token
from ...crud.crud_users import crud_users
from ...models.user import UserRead, UserNonce, SignatureVerificationRequest
from ...core.address_verification import verify_signature, generate_random
from ...core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
)

router = APIRouter(tags=["connect_wallet"])

@router.get("/auth/nonce/{public_address}")
async def fetch_user_nonce(
    request: Request,
    public_address: str, 
    db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any]:
    if not w3.is_address(public_address):
        raise HTTPException(status_code=400, detail="Invalid Ethereum address")
    
    public_address = public_address.lower()
    wallet: dict | None = await crud_users.get(
        db, public_address="0xa6e562AB21F6c83D99C9b624B4F50AFC48e6db68"
    )
    # Create new user if it does not exist
    if wallet is None:
        #return "Hello"
        return {"Try harder": "Bro"}
        """nonce = generate_random()
        user_data = {"public_address": public_address, "nonce": nonce}
        new_user = await crud_users.create(db=db, object=user_data)
        
        return UserNonce(nonce=new_user.nonce)"""

    # Return the nonce of the existing user
    #return UserNonce(nonce=wallet.nonce)
    return wallet


@router.post("/user/connect", response_model=Token, status_code=201)
async def connect_user_wallet(
    request: Request,
    response: Response,
    user_data: SignatureVerificationRequest,
    db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict:
    """
    Connect a wallet to the application.
    - If the user is connecting their wallet for the first time, they are added to the database.
    - If the wallet is already connected, a session is established without creating a new user record.
    
    Args:
        request (Request): The incoming request object.
        response (Response): The response object.
        user_data (SignatureVerificationRequest): The user data containing the public address and signature.
        db (AsyncSession): The database session.
    
    Returns:
        dict: The user's information along with a session token.
    """
    fetched_user: UserNonce = await crud_users.get(
        db=db, schema_to_select=UserNonce, public_address=user_data.public_address, is_deleted=False
    )
    
    # Ensure user exists
    if not fetched_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    nonce = fetched_user.nonce

    # Attempt to verify the signature
    try:
        verify_signature(nonce=nonce, signature=user_data.signature, public_address=user_data.public_address)
    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Signature verification failed")

    # If verification passed, authenticate and generate tokens
    db_user = await authenticate_user(public_address=user_data.public_address, db=db)
    
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

    # Update the nonce after successful login
    new_nonce = generate_random()
    await crud_users.update(db=db, object={"nonce": new_nonce}, id=db_user["id"])

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