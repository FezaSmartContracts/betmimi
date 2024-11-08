from datetime import datetime
from typing import Optional, List

from sqlmodel import (
    Column, SQLModel, Field, Relationship, TIMESTAMP, text, DECIMAL, UniqueConstraint
)



class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    public_address: str = Field(
        ..., unique=True, min_length=42, max_length=42, index=True, schema_extra={"example": "0x...fg"}
    )
    nonce: str = Field(default=None, index=True)
    balance: float = Field(
        sa_column=Column(DECIMAL(precision=10, scale=2), default=0.00, index=True)
    )
    prev_block_number: int = Field(default=0, index=True)
    latest_block_number: int = Field(default=0, index=True)
    is_superuser: bool = Field(default=False)
    is_admin: bool = Field(default=False)
    email: Optional[str] = Field(nullable=True, unique=True, schema_extra={"example": "moses@example.com"})
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

    predictions: List["Prediction"] = Relationship(back_populates="user")




class Prediction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    index: int = Field(index=True)
    layer: str = Field(index=True)
    hash_identifier: str = Field(unique=True, nullable=False, index=True)
    contract_address: str = Field(index=True)
    match_id: int = Field(index=True)
    result: int = Field(index=True)
    amount: float = Field(
        sa_column=Column(DECIMAL(precision=10, scale=2), default=0.00, index=True)
    )
    settled: bool = Field(default=False, index=True)
    total_opponent_wager: float = Field(
        sa_column=Column(DECIMAL(precision=10, scale=2), default=0.00, index=True)
    )
    f_matched: bool = Field(default=False, index=True)
    p_matched: bool = Field(default=False, index=True)
    for_sale: bool = Field(default=False, index=True)
    sold: bool = Field(default=False, index=True)
    price: Optional[float] = Field(
        sa_column=Column(DECIMAL(precision=10, scale=2), default=0.00, index=True)
    )
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
    opponents: List["Opponent"] = Relationship(back_populates="prediction")



class Opponent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prediction_id: int = Field(foreign_key="prediction.id")
    match_id: int = Field(index=True)
    prediction_index: int = Field(index=True)
    opponent_address: str = Field(index=True)
    opponent_wager: float = Field(
        sa_column=Column(DECIMAL(precision=10, scale=2), default=0.00, index=True)
    )
    result: int = Field(index=True)
    block_number: int = Field(index=True)
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
