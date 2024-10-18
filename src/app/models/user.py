from datetime import datetime
from typing import Optional, List

from sqlmodel import Column, SQLModel, Field, Relationship, TIMESTAMP, text



class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    public_address: str = Field(..., unique=True, min_length=42, max_length=42, schema_extra={"example": "0x...fg"})
    nonce: str = Field(default=None)
    is_superuser: bool = Field(default=False)
    email: Optional[str] = Field(..., nullable=True, unique=True, schema_extra={"example": "moses@example.com"})
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

    balance: Optional["UserBalance"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "joined"})
    predictions: List["Prediction"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "joined"})



class UserBalance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    amount: float = Field(default=0.0)
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

    user: Optional["User"] = Relationship(back_populates="balance")




class Prediction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    index: int = Field(index=True)
    layer: str = Field(index=True)
    match_id: int = Field(index=True)
    result: int = Field(index=True)
    amount: int = Field(index=True)
    settled: bool = Field(default=False, index=True)
    total_opponent_wager: int = Field(default=0, index=True)
    f_matched: bool = Field(default=False, index=True)
    p_matched: bool = Field(default=False, index=True)
    for_sale: bool = Field(default=False, index=True)
    sold: bool = Field(default=False, index=True)
    price: Optional[int] = Field(default=None, index=True)
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

    user: Optional["User"] = Relationship(back_populates="predictions")
    opponents: List["Opponent"] = Relationship(back_populates="prediction", sa_relationship_kwargs={"lazy": "joined"})





class Opponent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prediction_id: int = Field(foreign_key="prediction.id")
    opponent_address: str
    opponent_wager: int
    result: int
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

    prediction: Optional["Prediction"] = Relationship(back_populates="opponents")
