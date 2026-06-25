import asyncio

import boto3

from app.core.config import settings


s3_client = boto3.client(
    "s3",
    endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=settings.R2_ACCESS_KEY_ID,
    aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    region_name="auto",
)


async def upload_audio(file_bytes: bytes, filename: str) -> str:
    key = f"audio/{filename}"

    await asyncio.to_thread(
        s3_client.put_object,
        Bucket=settings.R2_BUCKET_NAME,
        Key=key,
        Body=file_bytes,
        ContentType="audio/wav",
    )

    return (
        f"https://{settings.R2_BUCKET_NAME}."
        f"{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com/{key}"
    )