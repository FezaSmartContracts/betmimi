from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.types import JSON
from uuid import uuid4

from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator


class UserBase(SQLModel):
    public_address: str = Field(..., unique=True, min_length=42, max_length=42, schema_extra={"example": "0x...fg"})


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    is_superuser: bool = Field(default=False)
    email: Optional[str] = Field(..., nullable=True, unique=True, schema_extra={"example": "moses@example.com"})
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    predictions: List[int] = Relationship(back_populates="user")
    balance: int = Relationship(back_populates="user")


class UserRead(SQLModel):
    id: int
    public_address: str

class UserReadInternal(UserRead):
    email: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserEmailUpdate(SQLModel):
    email: Optional[str] = None

class UserUpdateInternal(UserEmailUpdate):
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

