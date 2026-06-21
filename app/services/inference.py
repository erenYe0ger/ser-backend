import httpx
from fastapi import HTTPException

from app.core.config import settings


async def get_prediction(file_bytes: bytes, filename: str) -> dict:
    # Prepare the multipart form-data payload with the audio file
    files = {
        "file": (filename, file_bytes, "audio/wav")
    }

    try:
        # Send the audio file to the Hugging Face Spaces prediction endpoint
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.HF_SPACES_URL}/predict",
                files=files,
            )

        # Raise an exception for non-successful HTTP responses
        response.raise_for_status()

        # Parse and return the JSON prediction result
        return response.json()

    except Exception as exc:
        # Convert any upstream failure into a FastAPI 502 error
        raise HTTPException(
            status_code=502,
            detail="Failed to get prediction from inference service",
        ) from exc