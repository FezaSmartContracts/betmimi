from fastcrud import FastCRUD

from ..models.predictions import (
    Prediction, PredictionUpdateInternal, 
    PredictionUpdate, PredictionCreate
)

CRUDUser = FastCRUD[
    Prediction, PredictionCreate, PredictionUpdate,
    PredictionUpdateInternal, None
]

crud_predictions = CRUDUser(Prediction)
