from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from ..models.user import User, Prediction


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

class UserNonce(SQLModel):
    nonce: str

class UserCreate(SQLModel):
    public_address: str
    nonce: str

class UserEmailUpdate(SQLModel):
    email: Optional[str] = None

class UserUpdate(SQLModel):
    nonce: str

class UpdateUserBalance(SQLModel):
    balance: float

class UserUpdateInternal(UserUpdate):
    pass

class AdminUpdate(SQLModel):
    is_superuser: bool

#-----------Balance schemas-------------#

class UserBalanceRead(SQLModel):
    public_address: str
    amount: float
