from fastcrud import FastCRUD

from ..models.user import UserBalance
from ..schemas.users import (
    UserBalanceCreate,
    UserBalanceUpdateInternal, UserBalanceUpdate
)

CRUDUser = FastCRUD[
    UserBalance, UserBalanceCreate,
    UserBalanceUpdate, UserBalanceUpdateInternal, None
]

crud_balances = CRUDUser(UserBalance)
