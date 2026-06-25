from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    # Unique identifier for the prediction record
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Name of the uploaded audio file
    audio_filename: Mapped[str] = mapped_column(String, nullable=False)

    # Predicted emotion label
    emotion: Mapped[str] = mapped_column(String, nullable=False)

    # Confidence score for the predicted emotion
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Full emotion probability distribution as a JSON object
    all_emotions: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Cloudflare R2 public URL for the uploaded audio file
    audio_url: Mapped[str | None] = mapped_column(String, nullable=True)

    # Timeline emotion analysis data
    # Format:
    # [
    #   {
    #     "start_time": float,
    #     "end_time": float,
    #     "emotion": str,
    #     "confidence": float
    #   }
    # ]
    timeline_data: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Timestamp when the prediction was created (UTC)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    # User who created the prediction (nullable for existing records)
    user_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("users.id"),
        nullable=True,
    )