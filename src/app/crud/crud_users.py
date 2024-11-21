from fastcrud import FastCRUD

from app.models.user import User
from app.schemas.users import (
    UserCreate, UserUpdate,
    UserUpdateInternal
)

CRUDUser = FastCRUD[User, UserCreate, UserUpdate, UserUpdateInternal, None]

crud_users = CRUDUser(User)
