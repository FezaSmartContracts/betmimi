from fastcrud import FastCRUD

from ..models.balances import UserBalance, UserBalanceRead, UserBalanceUpdate

CRUDUser = FastCRUD[UserBalance, UserBalanceRead, UserBalanceUpdate]

crud_balances = CRUDUser(UserBalance)
