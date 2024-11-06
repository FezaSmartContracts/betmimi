from typing import Optional
from sqlmodel import SQLModel


class GameStatusUpdate(SQLModel):
    resolved: bool

class GameCreate(SQLModel):
    match_id: int
    resolved: bool

class GameIdRead(SQLModel):
    match_id: int

class GameRead(SQLModel):
    match_id: int
    resolved: bool

class GameUpdate(SQLModel):
    pass

class GameCreateInternal(GameUpdate):
    pass