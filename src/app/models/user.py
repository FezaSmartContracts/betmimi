from datetime import datetime, timezone
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class UserBase(SQLModel):
    public_address: str = Field(..., unique=True, min_length=42, max_length=42, schema_extra={"example": "0x...fg"})


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nonce: str = Field(default=None)
    is_superuser: bool = Field(default=False)
    email: Optional[str] = Field(..., nullable=True, unique=True, schema_extra={"example": "moses@example.com"})
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    predictions: List["Prediction"] = Relationship(back_populates="user")
    balance: "UserBalance" = Relationship(back_populates="user")


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


class UserBalance(SQLModel, table=True):
    balance_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    balance: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    user: Optional["User"] = Relationship(back_populates="balance")


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

    user: Optional["User"] = Relationship(back_populates="predictions")
    opponents: List["Opponent"] = Relationship(back_populates="prediction")

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


class Opponent(SQLModel, table=True):
    opponent_id: Optional[int] = Field(default=None, primary_key=True)
    prediction_id: int = Field(foreign_key="prediction.prediction_id")
    opponent_address: str
    opponent_wager: int
    result: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    prediction: Prediction = Relationship(back_populates="opponents")


class OpponentCreate(SQLModel):
    prediction_id: int
    opponent_address: str
    opponent_wager: int
    result: int


class OpponentRead(SQLModel):
    opponent_id: int
    prediction_id: int
    opponent_address: str
    opponent_wager: int
    result: int
    prediction: Prediction


class OpponentUpdate(SQLModel):
    opponent_address: str
    opponent_wager: int
    result: int


class OpponentUpdateInternal(OpponentUpdate):
    pass