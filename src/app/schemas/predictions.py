from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from ..models.user import Opponent


#-----------Prediction schemas-----------#
class PredictionCreate(SQLModel):
    user_id: int
    index: int
    layer: str
    hash_identifier: str
    match_id: int
    contract_address: str
    result: int
    amount: float
    settled: bool = False
    total_opponent_wager: float = 0.00
    f_matched: bool = False
    p_matched: bool = False
    for_sale: bool = False
    sold: bool = False
    price: Optional[float] = None

class QuickPredRead(SQLModel):
    id: int
    index: int
    hash_identifier: str
    match_id: int
    contract_address: str
    total_opponent_wager: float
    amount: float

class OppPredUpdate(SQLModel):
    total_opponent_wager: float
    f_matched: bool
    p_matched: bool

class PredSettledUpdate(SQLModel):
    settled: bool

class PredSoldUpdate(SQLModel):
    layer: str

class PredPriceUpdate(SQLModel):
    price: float

class PredInitialUpdate(SQLModel):
    for_sale: bool
    price: float

class PredictionRead(SQLModel):
    id: int
    user_id: int
    index: int
    layer: str
    match_id: int
    result: int
    amount: float
    settled: bool
    total_opponent_wager: float
    f_matched: bool
    p_matched: bool
    for_sale: bool
    sold: bool
    price: float
    created_at: datetime
    updated_at: Optional[datetime]

class PredictionAndOpponents(SQLModel):
    id: int
    user_id: int
    index: int
    layer: str
    match_id: int
    result: int
    amount: float
    created_at: datetime
    


class PredictionUpdate(SQLModel):
    layer: str
    settled: bool
    total_opponent_wager: float
    f_matched: bool
    p_matched: bool
    for_sale: bool
    sold: bool
    price: Optional[float]

class PredictionUpdateInternal(PredictionUpdate):
    pass
