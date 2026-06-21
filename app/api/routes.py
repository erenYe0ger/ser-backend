import hashlib

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.prediction import Prediction
from app.services.cache import get_cached_result, set_cached_result
from app.services.inference import get_prediction

router = APIRouter()


@router.post("/predict")
async def predict(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # Read the uploaded audio file into memory
    file_bytes = await file.read()

    # Compute a SHA-256 hash of the file contents for cache lookup
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    # Check whether a prediction already exists in Redis
    cached_result = await get_cached_result(file_hash)

    # Return cached result immediately if found
    if cached_result is not None:
        return {
            **cached_result,
            "source": "cache",
        }

    # Request a fresh prediction from the HF Spaces inference service
    result = await get_prediction(
        file_bytes=file_bytes,
        filename=file.filename or "audio.wav",
    )

    # Store the prediction result in PostgreSQL
    prediction = Prediction(
        audio_filename=file.filename or "audio.wav",
        emotion=result["emotion"],
        confidence=result["confidence"],
        all_emotions=result["all_emotions"],
    )

    db.add(prediction)
    await db.commit()
    await db.refresh(prediction)

    # Cache the prediction result in Redis for future requests
    await set_cached_result(file_hash, result)

    # Return the model-generated result
    return {
        **result,
        "source": "model",
    }


@router.get("/history")
async def get_history(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    # Fetch the most recent predictions ordered by creation time
    stmt = (
        select(Prediction)
        .order_by(Prediction.created_at.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    predictions = result.scalars().all()

    # Convert ORM objects into serializable dictionaries
    return [
        {
            "id": prediction.id,
            "audio_filename": prediction.audio_filename,
            "emotion": prediction.emotion,
            "confidence": prediction.confidence,
            "created_at": prediction.created_at,
        }
        for prediction in predictions
    ]