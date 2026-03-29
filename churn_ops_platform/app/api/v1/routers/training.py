from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.v1.schemas.training import RetrainResponse
from app.services.training_service import TrainingService

router = APIRouter()

training_service = TrainingService()


@router.post("/training/retrain", response_model=RetrainResponse)
def retrain_model(file: UploadFile = File(...)) -> RetrainResponse:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    try:
        return training_service.retrain_from_csv(file.file.read(), filename=file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
