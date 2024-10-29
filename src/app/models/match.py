from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import (
    Column, SQLModel, Field, TIMESTAMP, text, DECIMAL
)

class GameStatus(str, Enum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    provider_id: int = Field(nullable=False)
    home_team: str = Field(..., index=True)
    away_team: str = Field(..., index=True)
    start_time: datetime
    end_time: Optional[datetime] = None
    status: GameStatus = Field(default=GameStatus.SCHEDULED)
    score_home: Optional[int] = None
    score_away: Optional[int] = None
    winner: Optional[str] = None 
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    updated_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    ))