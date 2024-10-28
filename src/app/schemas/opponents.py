from sqlmodel import SQLModel

#---------------Opponent schemas------------#
class OpponentCreate(SQLModel):
    prediction_id: int
    opponent_address: str
    opponent_wager: int
    result: int


class OpponentRead(SQLModel):
    id: int
    prediction_id: int
    opponent_address: str
    opponent_wager: int
    result: int

class OpponentUpdate(SQLModel):
    opponent_address: str
    opponent_wager: int
    result: int

class OpponentUpdateInternal(OpponentUpdate):
    pass

class BackerAddress(SQLModel):
    public_address: str