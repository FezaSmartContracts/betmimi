from fastcrud import FastCRUD

from app.models.user import Opponent
from app.schemas.opponents import (
    OpponentCreate, OpponentUpdateInternal, OpponentUpdate
)

CRUDUser = FastCRUD[
    Opponent, OpponentCreate,
    OpponentUpdate, OpponentUpdateInternal, None
]

crud_opponent = CRUDUser(Opponent)
