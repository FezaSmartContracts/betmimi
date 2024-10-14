from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User


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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    def __init_subclass__(cls, **kwargs):
        # Define relationships after subclass initialization
        cls.user: Optional["User"] = Relationship(back_populates="predictions")
        super().__init_subclass__(**kwargs)


class Opponent(SQLModel, table=True):
    opponent_id: Optional[int] = Field(default=None, primary_key=True)
    prediction_id: int = Field(foreign_key="prediction.prediction_id")
    opponent_address: str
    opponent_wager: int
    result: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    prediction: Prediction = Relationship(back_populates="opponents")

class PredictionCreate(SQLModel):
    user_id: int
    index: int
    layer: str
    match_id: int
    result: int
    amount: int
    settled: bool = False
    total_opponent_wager: int = 0
    f_matched: bool = False
    p_matched: bool = False
    for_sale: bool = False
    sold: bool = False
    price: Optional[int] = None

class OpponentCreate(SQLModel):
    prediction_id: int
    opponent_address: str
    opponent_wager: int
    result: int

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
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PredictionUpdateInternal(PredictionUpdate):
    pass

class OpponentUpdate(SQLModel):
    opponent_address: str
    opponent_wager: int
    result: int

class OpponentUpdateInternal(OpponentUpdate):
    pass



