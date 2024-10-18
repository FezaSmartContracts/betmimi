from fastcrud import FastCRUD

from ..models.user import User
from ..schemas.users import (
    UserCreate, UserEmailUpdate,
    UserUpdateInternal
)

CRUDUser = FastCRUD[User, UserCreate, UserEmailUpdate, UserUpdateInternal, None]

crud_users = CRUDUser(User)
