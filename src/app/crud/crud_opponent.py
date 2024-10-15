from fastcrud import FastCRUD

from ..models.user import (
    Opponent, OpponentCreate, OpponentUpdateInternal, OpponentUpdate
)

CRUDUser = FastCRUD[
    Opponent, OpponentCreate,
    OpponentUpdate, OpponentUpdateInternal, None
]

crud_balances = CRUDUser(Opponent)
