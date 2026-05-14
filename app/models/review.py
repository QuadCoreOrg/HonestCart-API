from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Review(BaseModel):
    id: str
    text: str
    rating: int = Field(..., ge=1, le=5)
    date: datetime
    user_hash: str
    verified_purchase: bool = False
    helpful_count: int = 0

    # Analiz sonuçları
    bot_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    sentiment: Optional[str] = None  # positive/negative/neutral
    categories: Optional[list[str]] = None


class ReviewPreprocessor:
    @staticmethod
    def clean_text(text: str) -> str:
        import re

        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text