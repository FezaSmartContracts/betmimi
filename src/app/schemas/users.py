from sqlmodel import SQLModel
from typing import Optional
from ..models.user import Prediction


#-------------User schemas--------------------#
class SignatureVerificationRequest(SQLModel):
    signature: str
    public_address: str

class UserRead(SQLModel):
    id: int
    public_address: str
    balance: float

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
    prev_block_number: int
    latest_block_number: int

class UserUpdateInternal(UserUpdate):
    pass

class AdminUpdate(SQLModel):
    is_admin: bool

#-----------Balance schemas-------------#

class UserBalanceRead(SQLModel):
    public_address: str
    balance: float
    prev_block_number: int
    latest_block_number: int

class QuickBalanceRead(SQLModel):
    balance: int

class QuickUpdateUserBalance(SQLModel):
    balance: int

class QuickAdminRead(SQLModel):
    public_address: str
    is_admin: bool
    email: str
