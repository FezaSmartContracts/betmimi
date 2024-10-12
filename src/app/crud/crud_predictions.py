from fastcrud import FastCRUD

from ..models.predictions import Prediction, PredictionRead, PredictionUpdate

CRUDUser = FastCRUD[Prediction, PredictionRead, PredictionUpdate]

crud_predictions = CRUDUser(Prediction)
