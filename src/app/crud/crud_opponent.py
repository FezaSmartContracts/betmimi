from fastcrud import FastCRUD

from ..models.user import Opponent
from ..schemas.opponents import (
    OpponentCreate, OpponentUpdateInternal, OpponentUpdate
)

CRUDUser = FastCRUD[
    Opponent, OpponentCreate,
    OpponentUpdate, OpponentUpdateInternal, None
]

crud_opponent = CRUDUser(Opponent)
