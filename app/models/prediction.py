from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, JSON, String
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
    all_emotions: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Timestamp when the prediction was created (UTC)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )