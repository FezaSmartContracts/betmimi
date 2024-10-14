from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .balances import UserBalance 
    from .predictions import Prediction


class UserBase(SQLModel):
    public_address: str = Field(..., unique=True, min_length=42, max_length=42, schema_extra={"example": "0x...fg"})


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nonce: str = Field(default=None)
    is_superuser: bool = Field(default=False)
    email: Optional[str] = Field(..., nullable=True, unique=True, schema_extra={"example": "moses@example.com"})
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    def __init_subclass__(cls, **kwargs):
        # Define relationships after subclass initialization
        cls.predictions: List["Prediction"] = Relationship(back_populates="user")
        cls.balance: "UserBalance" = Relationship(back_populates="user")
        super().__init_subclass__(**kwargs)

class SignatureVerificationRequest(SQLModel):
    signature: str
    public_address: str

class UserRead(SQLModel):
    id: int
    public_address: str

class UserReadInternal(UserRead):
    email: Optional[str] = None

class UserNonce(SQLModel):
    nonce: str

class UserCreate(UserBase):
    pass

class UserEmailUpdate(SQLModel):
    email: Optional[str] = None

class UserUpdateInternal(UserEmailUpdate):
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

