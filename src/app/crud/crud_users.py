from fastcrud import FastCRUD

from ..models.user import (
    User, UserCreate, UserEmailUpdate,
    UserUpdateInternal
)

CRUDUser = FastCRUD[User, UserCreate, UserEmailUpdate, UserUpdateInternal, None]

crud_users = CRUDUser(User)
