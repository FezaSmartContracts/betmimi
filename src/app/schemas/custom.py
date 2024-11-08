from sqlmodel import SQLModel

class Date(SQLModel):
    year: int
    month: int
    day: int

class Count(SQLModel):
    number: int