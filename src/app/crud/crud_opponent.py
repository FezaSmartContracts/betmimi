from fastcrud import FastCRUD

from ..models.predictions import (
    Opponent, OpponentCreate, OpponentUpdateInternal, OpponentUpdate
)

CRUDUser = FastCRUD[
    Opponent, OpponentCreate,
    OpponentUpdate, OpponentUpdateInternal, None
]

crud_balances = CRUDUser(Opponent)
