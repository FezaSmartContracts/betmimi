from fastcrud import FastCRUD

from ..models.user import User
from ..schemas.users import (
    UserCreate, UserUpdate,
    UserUpdateInternal
)

CRUDUser = FastCRUD[User, UserCreate, UserUpdate, UserUpdateInternal, None]

crud_users = CRUDUser(User)
