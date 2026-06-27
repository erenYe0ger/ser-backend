import asyncio
import hashlib
from collections import Counter

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.prediction import Prediction
from app.services.cache import get_cached_result, set_cached_result
from app.services.chunker import chunk_audio
from app.services.inference import get_prediction
from app.services.r2 import upload_audio

router = APIRouter()


@router.post("/predict")
async def predict(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Read the uploaded audio file into memory
    file_bytes = await file.read()

    # Compute a SHA-256 hash of the file contents for cache lookup
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    # Check whether a prediction already exists in Redis
    cached_result = await get_cached_result(file_hash)

    # If found in cache, still save a prediction record
    if cached_result is not None:
        prediction = Prediction(
            audio_filename=file.filename or "audio.wav",
            emotion=cached_result["emotion"],
            confidence=cached_result["confidence"],
            all_emotions=cached_result["all_emotions"],
            user_id=current_user["sub"],
        )

        db.add(prediction)
        await db.commit()
        await db.refresh(prediction)

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
        user_id=current_user["sub"],
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


@router.post("/predict/timeline")
async def predict_timeline(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    file_bytes = await file.read()
    filename = file.filename or "audio.wav"

    # Upload original audio to Cloudflare R2
    audio_url = await upload_audio(file_bytes, filename)

    # Chunk audio in a worker thread
    chunks = await asyncio.to_thread(chunk_audio, file_bytes)

    semaphore = asyncio.Semaphore(5)

    async def process_chunk(chunk: dict):
        async with semaphore:
            try:
                chunk_hash = hashlib.sha256(
                    chunk["audio_bytes"]
                ).hexdigest()

                cached_result = await get_cached_result(chunk_hash)
                if cached_result is not None:
                    return cached_result, True

                result = await get_prediction(
                    chunk["audio_bytes"],
                    "chunk.wav",
                )

                await set_cached_result(chunk_hash, result)

                return result, False

            except Exception:
                return None, False

    results = await asyncio.gather(
        *(process_chunk(chunk) for chunk in chunks)
    )

    all_from_cache = all(
        from_cache
        for result, from_cache in results
        if result is not None
    )

    timeline_data = []

    for chunk, item in zip(chunks, results):
        result, _ = item

        if result is None:
            continue

        timeline_data.append(
            {
                "start_time": chunk["start_ms"] / 1000.0,
                "end_time": chunk["end_ms"] / 1000.0,
                "emotion": result["emotion"],
                "confidence": result["confidence"],
            }
        )

    if timeline_data:
        dominant_emotion = Counter(
            item["emotion"] for item in timeline_data
        ).most_common(1)[0][0]

        average_confidence = (
            sum(item["confidence"] for item in timeline_data)
            / len(timeline_data)
        )
    else:
        dominant_emotion = "unknown"
        average_confidence = 0.0

    prediction = Prediction(
        audio_filename=filename,
        emotion=dominant_emotion,
        confidence=average_confidence,
        all_emotions=None,
        audio_url=audio_url,
        timeline_data=timeline_data,
        user_id=(
            current_user["sub"]
            if current_user["user_type"] != "guest"
            else None
        ),
    )

    db.add(prediction)
    await db.commit()
    await db.refresh(prediction)

    return {
        "audio_url": audio_url,
        "timeline_data": timeline_data,
        "emotion": dominant_emotion,
        "confidence": average_confidence,
        "source": "cache" if all_from_cache else "model",
    }


@router.get("/history")
async def get_history(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Fetch the most recent predictions ordered by creation time
    stmt = (
        select(Prediction)
        .where(Prediction.user_id == current_user["sub"])
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
            "audio_url": prediction.audio_url,
            "timeline_data": prediction.timeline_data,
        }
        for prediction in predictions
    ]