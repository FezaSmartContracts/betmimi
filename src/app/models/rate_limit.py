from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, text, TIMESTAMP, Column


def sanitize_path(path: str) -> str:
    return path.strip("/").replace("/", "_")


class RateLimitBase(SQLModel):
    path: str = Field(..., schema_extra={"example": "users"})
    limit: int = Field(..., schema_extra={"example": 5})
    period: int = Field(..., schema_extra={"example": 60})

    @classmethod
    def validate_path(cls, v: str) -> str:
        return sanitize_path(v)


class RateLimit(RateLimitBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None, schema_extra={"example": "users:5:60"})
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    updated_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    ))


class RateLimitRead(RateLimitBase):
    id: int
    name: str


class RateLimitCreate(RateLimitBase):
    name: Optional[str] = Field(default=None, schema_extra={"example": "api_usdtv1_users:5:60"})

class RateLimitCreateInternal(RateLimitCreate):
    pass


class RateLimitUpdate(SQLModel):
    path: Optional[str] = Field(default=None)
    limit: Optional[int] = None
    period: Optional[int] = None
    name: Optional[str] = None

    @classmethod
    def validate_path(cls, v: Optional[str]) -> Optional[str]:
        return sanitize_path(v) if v is not None else None


class RateLimitUpdateInternal(RateLimitUpdate):
    pass

class RateLimitDelete(SQLModel):
    pass
