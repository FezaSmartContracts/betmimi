from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from ..models.user import User, UserBalance, Prediction


#-------------User schemas--------------------#
class SignatureVerificationRequest(SQLModel):
    signature: str
    public_address: str

class UserRead(SQLModel):
    id: int
    public_address: str

class UserPredictionRead(SQLModel):
    id: int
    public_address: str
    predictions: list["Prediction"]

class UserReadNonce(UserRead):
    nonce: str

class UserPublicAddress(SQLModel):
    public_address: str

class UserReadInternal(UserRead):
    email: Optional[str] = None
    nonce: str

class ReadUserBalance(SQLModel):
    id: int
    public_address: str
    created_at: datetime
    updated_at: datetime
    balance: "UserBalance"

class UserNonce(SQLModel):
    nonce: str

class UserCreate(SQLModel):
    public_address: str
    nonce: Optional[str] = Field(default=None)

class UserEmailUpdate(SQLModel):
    email: Optional[str] = None

class UserUpdateInternal(UserEmailUpdate):
    nonce: str

class AdminUpdate(SQLModel):
    is_superuser: bool

#-----------Balance schemas-------------#
class UserBalanceUpdate(SQLModel):
    amount: float = Field(default=0.0)

class UserBalanceRead(SQLModel):
    amount: float

class UserBalanceCreate(SQLModel):
    user_id: int
    amount: float

class UserBalanceUpdateInternal(UserBalanceUpdate):
    pass