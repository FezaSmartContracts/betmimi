from fastcrud import FastCRUD

from app.models.user import Prediction
from app.schemas.predictions import (
    PredictionUpdateInternal, 
    PredictionUpdate, PredictionCreate
)

CRUDUser = FastCRUD[
    Prediction, PredictionCreate, PredictionUpdate,
    PredictionUpdateInternal, None
]

crud_predictions = CRUDUser(Prediction)
