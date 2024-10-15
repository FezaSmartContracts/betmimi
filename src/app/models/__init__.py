'''from sqlmodel import SQLModel
from app.models.user import User, UserBalance, Prediction
from app.models.rate_limit import RateLimit
from app.core.db.token_blacklist import TokenBlacklist

from app.core.db.database import async_engine

# Consolidate all models’ metadata
SQLModel.metadata.create_all(bind=async_engine)'''
