from fastcrud import FastCRUD

from ..models.user import (
    Prediction, PredictionUpdateInternal, 
    PredictionUpdate, PredictionCreate
)

CRUDUser = FastCRUD[
    Prediction, PredictionCreate, PredictionUpdate,
    PredictionUpdateInternal, None
]

crud_predictions = CRUDUser(Prediction)
