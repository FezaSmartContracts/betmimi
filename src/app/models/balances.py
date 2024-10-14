from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User


class UserBalance(SQLModel, table=True):
    balance_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    balance: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    def __init_subclass__(cls, **kwargs):
        # Define relationships after subclass initialization
        cls.user: Optional["User"] = Relationship(back_populates="balance")
        super().__init_subclass__(**kwargs)

class UserBalanceUpdate(SQLModel):
    balance: float = Field(default=0.0)
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserBalanceRead(SQLModel):
    balance: float

class UserBalanceCreate(SQLModel):
    user_id: int
    balance: float

class UserBalanceUpdateInternal(UserBalanceUpdate):
    pass
    

