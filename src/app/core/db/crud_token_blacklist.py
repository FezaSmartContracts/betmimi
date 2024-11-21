from fastcrud import FastCRUD

from app.core.db.token_blacklist import TokenBlacklist
from app.core.schemas import TokenBlacklistCreate, TokenBlacklistUpdate

CRUDTokenBlacklist = FastCRUD[TokenBlacklist, TokenBlacklistCreate, TokenBlacklistUpdate, TokenBlacklistUpdate, None]
crud_token_blacklist = CRUDTokenBlacklist(TokenBlacklist)
