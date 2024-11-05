from sqlmodel import SQLModel

class ArbUsdtv1FallBack(SQLModel):
    name: str
    from_block: int
    to_block: int