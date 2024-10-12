from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class UserBalance(SQLModel, table=True):
    balance_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    balance: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(datetime.timezone.utc))
    updated_at: Optional[datetime] = None

    user: Optional[int] = Relationship(back_populates="balance")

class UserBalanceUpdate(SQLModel):
    balance: float = Field(default=0.0)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now(datetime.timezone.utc))

class UserBalanceRead(SQLModel):
    balance: float
    

