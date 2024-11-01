from fastcrud import FastCRUD

from ..models.games import Game
from ..schemas.games import (
    GameCreate,
    GameStatusUpdate,
    GameCreateInternal
)

CRUDUser = FastCRUD[
    Game, GameCreate,GameStatusUpdate, GameCreateInternal, None
]

crud_matches = CRUDUser(Game)
