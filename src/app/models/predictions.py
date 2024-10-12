from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Prediction(SQLModel, table=True):
    prediction_id: Optional[int] = Field(default=None, primary_key=True)
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(datetime.timezone.utc))
    updated_at: Optional[datetime] = None

    user: Optional[int] = Relationship(back_populates="predictions")
    opponents: List["Opponent"] = Relationship(back_populates="prediction")


class Opponent(SQLModel, table=True):
    opponent_id: Optional[int] = Field(default=None, primary_key=True)
    prediction_id: int = Field(foreign_key="prediction.prediction_id")
    opponent_address: str
    opponent_wager: int
    result: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(datetime.timezone.utc))
    updated_at: Optional[datetime] = None

    prediction: Prediction = Relationship(back_populates="opponents")

class PredictionRead(SQLModel):
    prediction_id: int
    user_id: int
    index: int
    layer: str
    match_id: int
    result: int
    amount: int
    settled: bool
    total_opponent_wager: int
    f_matched: bool
    p_matched: bool
    for_sale: bool
    sold: bool
    price: int
    timestamp: datetime
    opponents: List["Opponent"]

class OpponentRead(SQLModel):
    opponent_id: int
    prediction_id: int
    opponent_address: str
    opponent_wager: int
    result: int
    prediction: Prediction


class PredictionUpdate(SQLModel):
    layer: str = Field(index=True)
    settled: bool = Field(default=False, index=True)
    total_opponent_wager: int = Field(default=0, index=True)
    f_matched: bool = Field(default=False, index=True)
    p_matched: bool = Field(default=False, index=True)
    for_sale: bool = Field(default=False, index=True)
    sold: bool = Field(default=False, index=True)
    price: Optional[int] = Field(default=None, index=True)
    updated_at: datetime = Field(default_factory=datetime.now(datetime.timezone.utc))

class OpponentUpdate(SQLModel):
    opponent_address: str
    opponent_wager: int
    result: int
    updated_at: datetime = Field(default_factory=datetime.now(datetime.timezone.utc))



