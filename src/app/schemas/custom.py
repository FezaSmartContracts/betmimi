from typing import List
from sqlmodel import SQLModel
from pydantic import EmailStr, BaseModel

class Date(SQLModel):
    year: int
    month: int
    day: int

class Count(SQLModel):
    number: int

class EmailSchema(BaseModel):
    email: List[EmailStr]
    subject: str
    body: str