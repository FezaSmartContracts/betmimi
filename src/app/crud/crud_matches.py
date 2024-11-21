from fastcrud import FastCRUD

from app.models.games import Game
from app.schemas.games import (
    GameCreate,
    GameStatusUpdate,
    GameCreateInternal
)

CRUDUser = FastCRUD[
    Game, GameCreate,GameStatusUpdate, GameCreateInternal, None
]

crud_matches = CRUDUser(Game)
