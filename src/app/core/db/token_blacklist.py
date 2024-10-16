from datetime import datetime
from sqlmodel import SQLModel, Field, Column, TIMESTAMP, text

class TokenBlacklist(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)
    token: str = Field(index=True, nullable=False, unique=True)
    expires_at: datetime = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
