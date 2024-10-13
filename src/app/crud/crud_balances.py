from fastcrud import FastCRUD

from ..models.balances import (
    UserBalance, UserBalanceCreate,
    UserBalanceCreateInternal, UserBalanceUpdate
)

CRUDUser = FastCRUD[
    UserBalance, UserBalanceCreate,
    UserBalanceCreateInternal, UserBalanceUpdate
]

crud_balances = CRUDUser(UserBalance)
