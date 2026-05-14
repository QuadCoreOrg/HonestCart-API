from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.models.review import Review


class RiskLevel(str, Enum):
    SAFE = "safe"
    CAUTION = "caution"
    RISKY = "risky"
    VERY_RISKY = "very_risky"


class ProductInfo(BaseModel):
    name: str
    image_url: str
    price: str
    platform: str  # trendyol/amazon/hepsiburada
    category: str


class CategoryAnalysis(BaseModel):
    name: str
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    positive_ratio: float = 0.0
    negative_ratio: float = 0.0
    neutral_ratio: float = 0.0
    sentiment_summary: str = ""


class TrendData(BaseModel):
    direction: str  # increasing/decreasing/stable
    change_percentage: float = 0.0
    alert: bool = False
    alert_message: str = ""


class AISummary(BaseModel):
    overall: str
    complaints: list[str] = []
    praises: list[str] = []
    warnings: list[str] = []


class SampleReviews(BaseModel):
    most_reliable_negative: list[Review] = []
    most_reliable_positive: list[Review] = []


class BotAnalysis(BaseModel):
    bot_percentage: float = 0.0
    suspicious_count: int = 0
    confidence: str = "medium"  # low/medium/high


class RatingAnalysis(BaseModel):
    platform_rating: float = 0.0
    real_estimated_rating: float = 0.0
    inflation_detected: bool = False


class DateRange(BaseModel):
    oldest: date
    newest: date


class ReviewStats(BaseModel):
    total_found: int = 0
    total_analyzed: int = 0
    date_range: Optional[DateRange] = None


class Sustainability(BaseModel):
    co2_saved_grams: float = 0.0
    message: str = ""


class AnalysisResult(BaseModel):
    id: str  # UUID
    cached: bool = False
    product: ProductInfo
    review_stats: ReviewStats
    bot_analysis: BotAnalysis
    rating_analysis: RatingAnalysis
    categories: dict[str, CategoryAnalysis] = {}
    trend: TrendData
    ai_summary: AISummary
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    risk_explanation: str
    sample_reviews: SampleReviews
    sustainability: Sustainability


# Request/Response schemas
class AnalyzeRequest(BaseModel):
    url: str


class AnalyzeResponse(BaseModel):
    analysis_id: str
    cached: bool
    product: ProductInfo
    review_stats: ReviewStats
    bot_analysis: BotAnalysis
    rating_analysis: RatingAnalysis
    categories: dict[str, CategoryAnalysis]
    trend: TrendData
    ai_summary: AISummary
    risk_score: int
    risk_level: RiskLevel
    risk_explanation: str
    sample_reviews: SampleReviews
    sustainability: Sustainability