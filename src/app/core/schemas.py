import uuid as uuid_pkg
from datetime import datetime

from pydantic import BaseModel


class HealthCheck(BaseModel):
    name: str
    version: str
    description: str


# -------------- token --------------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    public_address: str


class TokenBlacklistBase(BaseModel):
    token: str
    expires_at: datetime


class TokenBlacklistCreate(TokenBlacklistBase):
    pass


class TokenBlacklistUpdate(TokenBlacklistBase):
    pass
