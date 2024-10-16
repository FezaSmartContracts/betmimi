from fastapi import APIRouter, Depends, Request, Response
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import UnauthorizedException
from ...core.security import blacklist_token

router = APIRouter(tags=["connect_wallet"])

@router.post("/disconnect_wallet")
async def disconnect_user_wallet(
    request: Request, response: Response, db: AsyncSession = Depends(async_get_db)
) -> dict[str, str]:
    # Retrieve the access token from the Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedException("Missing or invalid Authorization header.")
    
    # Extract the token part after 'Bearer '
    access_token = auth_header.split(" ")[1]

    try:
        # Blacklist the access token to invalidate it
        await blacklist_token(token=access_token, db=db)
        
        # Delete the refresh token cookie
        response.delete_cookie(key="refresh_token")
        
        return {"message": "Disconnected successfully"}

    except JWTError:
        raise UnauthorizedException("Invalid or expired token.")
