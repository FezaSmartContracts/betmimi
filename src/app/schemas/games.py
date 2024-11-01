from typing import Optional
from sqlmodel import SQLModel
from enum import Enum
from datetime import datetime

class GameStatus(str, Enum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class GameStatusRead(SQLModel):
    id: int
    match_id: int
    status: Optional[GameStatus]

class GameStatusUpdate(SQLModel):
    status: GameStatus

class GameCreate(SQLModel):
    match_id: int

class GameIdRead(SQLModel):
    match_id: int

class GameUpdate(SQLModel):
    pass

class GameCreateInternal(GameUpdate):
    pass