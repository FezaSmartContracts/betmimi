from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from ..models.user import Opponent


#-----------Prediction schemas-----------#
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
    id: int
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
    created_at: datetime
    updated_at: Optional[datetime]

class PredictionAndOpponents(SQLModel):
    id: int
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
    created_at: datetime
    updated_at: Optional[datetime]
    oppononts: List[Opponent]
    


class PredictionUpdate(SQLModel):
    layer: str = Field(index=True)
    settled: bool = Field(default=False, index=True)
    total_opponent_wager: int = Field(default=0, index=True)
    f_matched: bool = Field(default=False, index=True)
    p_matched: bool = Field(default=False, index=True)
    for_sale: bool = Field(default=False, index=True)
    sold: bool = Field(default=False, index=True)
    price: Optional[int] = Field(default=None, index=True)

class PredictionUpdateInternal(PredictionUpdate):
    pass
