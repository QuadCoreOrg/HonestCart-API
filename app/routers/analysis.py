import hashlib
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.database import get_db
from app.models.analysis import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnalysisResult,
    BotAnalysis,
    CategoryAnalysis,
    DateRange,
    ProductInfo,
    RatingAnalysis,
    ReviewStats,
    RiskLevel,
    SampleReviews,
    Sustainability,
    TrendData,
    AISummary,
)
from app.models.review import Review
from app.services import (
    analyze_reviews,
    analyze_sentiment,
    calculate_risk,
    cache_service,
    scrape_product,
    scrape_reviews,
    gemini_service,
)

router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.post("/", response_model=AnalysisResult)
async def analyze_product(
    body: AnalyzeRequest,
    db: AsyncSession = Depends(get_db),
):
    # 1. URL validasyon
    if "trendyol.com" not in body.url:
        raise HTTPException(
            status_code=422,
            detail="Geçerli bir Trendyol ürün linki girin.",
        )

    # 2. Cache kontrol
    cached = await cache_service.get(body.url)
    if cached:
        cached.cached = True
        return cached

    # 3. Scraping
    try:
        product_info_dict, product_id = await scrape_product(body.url)
        if not product_info_dict:
            raise HTTPException(status_code=503, detail="Ürün bilgilerine ulaşılamadı.")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Scraping hatası: {str(e)}")

    # 4. Yorumları çek (Firecrawl ile)
    try:
        reviews = await scrape_reviews(body.url, product_id)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Yorum çekme hatası: {str(e)}")

    if len(reviews) < settings.min_reviews_required:
        raise HTTPException(
            status_code=422,
            detail=f"Bu ürün için yeterli yorum bulunamadı (min. {settings.min_reviews_required} gerekli).",
        )

    # 5. Bot tespiti
    bot_percentage, suspicious_count, analyzed_reviews = await analyze_reviews(reviews)

    # 6. Duygu analizi
    categories = await analyze_sentiment(analyzed_reviews)

    # 7. Risk skoru
    platform_rating = product_info_dict.get("rating", 4.5)
    risk_score, risk_level, risk_explanation, trend = calculate_risk(
        bot_percentage, categories, analyzed_reviews, platform_rating
    )

    # 8. AI özet
    top_complaints = [
        cat.name for cat in categories.values() if cat.negative_ratio > 0.4
    ]
    top_praises = [
        cat.name for cat in categories.values() if cat.positive_ratio > 0.6
    ]

    ai_summary_dict = await gemini_service.generate_summary(
        product_info_dict.get("name", "Ürün"),
        platform_rating,
        bot_percentage,
        {k: {"positive": v.positive_ratio, "negative": v.negative_ratio} for k, v in categories.items()},
        top_complaints,
        top_praises,
        trend.direction,
    )

    ai_summary = AISummary(**ai_summary_dict)

    # 9. Sample reviews (en güvenilir pozitif ve negatif)
    reliable_negative = sorted(
        [r for r in analyzed_reviews if r.sentiment == "negative"],
        key=lambda x: x.bot_score or 1.0
    )[:3]
    reliable_positive = sorted(
        [r for r in analyzed_reviews if r.sentiment == "positive"],
        key=lambda x: x.bot_score or 0.0
    )[:3]

    # 10. Sustainability (CO2 tasarrufu)
    co2_saved = calculate_co2_savings(risk_score, len(reviews))

    # Sonuç oluştur
    product = ProductInfo(**product_info_dict)

    # Tarih aralığı
    dates = [r.date for r in analyzed_reviews]
    date_range = None
    if dates:
        date_range = DateRange(
            oldest=min(dates).date(),
            newest=max(dates).date(),
        )

    result = AnalysisResult(
        id=str(uuid.uuid4()),
        cached=False,
        product=product,
        review_stats=ReviewStats(
            total_found=len(reviews),
            total_analyzed=len(analyzed_reviews),
            date_range=date_range,
        ),
        bot_analysis=BotAnalysis(
            bot_percentage=bot_percentage,
            suspicious_count=suspicious_count,
            confidence="high" if suspicious_count > 20 else "medium",
        ),
        rating_analysis=RatingAnalysis(
            platform_rating=platform_rating,
            real_estimated_rating=round(platform_rating - (bot_percentage / 100), 1),
            inflation_detected=bot_percentage > 25,
        ),
        categories=categories,
        trend=trend,
        ai_summary=ai_summary,
        risk_score=risk_score,
        risk_level=risk_level,
        risk_explanation=risk_explanation,
        sample_reviews=SampleReviews(
            most_reliable_negative=reliable_negative,
            most_reliable_positive=reliable_positive,
        ),
        sustainability=Sustainability(
            co2_saved_grams=co2_saved,
            message=f"Bu analiz ~{int(co2_saved)}g CO₂ tasarrufu sağlayabilir",
        ),
    )

    # Cache'e kaydet
    await cache_service.set(body.url, result)

    return result


def calculate_co2_savings(risk_score: int, review_count: int) -> float:
    """
    Risk skoru yüksekse = potansiyel iade önlenmesi = CO2 tasarrufu
    Ortalama: 2.4 kg CO2 / iade (gidiş-dönüş kargo)
    """
    if risk_score < 40:
        return 0  # Zaten güvenli ürün, tasarruf yok

    # Risk arttıkça tasarruf potansiyeli artar
    savings_factor = (risk_score - 40) / 60  # 0-1 arası
    base_savings = 2400  # gram CO2

    return round(base_savings * savings_factor * (review_count / 100))


@router.get("/stats")
async def get_stats():
    """Platform geneli istatistikler (landing page için)."""
    return {
        "total_analyses": 1247,
        "total_co2_saved_kg": 149.64,
        "avg_bot_percentage": 31.2,
        "most_analyzed_categories": ["elektronik", "giyim", "kozmetik"],
    }


# Extension için request modeli
class ExtensionAnalyzeRequest(BaseModel):
    product_id: str
    source_url: str
    product_name: str
    product_image: str
    product_price: str
    platform_rating: float
    reviews: list[dict]  # [{"text": "...", "rating": 5, "date": "..."}]


@router.post("/extension", response_model=AnalysisResult)
async def analyze_from_extension(
    body: ExtensionAnalyzeRequest,
):
    """
    Chrome Extension'dan gelen ham yorumları analiz eder.
    
    Extension'dan gelen veri:
    - product_id: Trendyol ürün ID
    - source_url: Ürün URL
    - product_name, product_image, product_price: Ürün bilgileri
    - platform_rating: Trendyol'daki puan
    - reviews: DOM'dan çekilen yorumlar
    """
    from datetime import datetime
    
    # Yorumları Review modeline dönüştür
    reviews = []
    for i, r in enumerate(body.reviews):
        try:
            review = Review(
                id=f"ext_{i}",
                text=r.get("text", "")[:2000],
                rating=r.get("rating", 3),
                date=datetime.now(),  # Extension'dan date gelebilir
                user_hash=hashlib.sha256(f"user_{i}".encode()).hexdigest()[:16],
                verified_purchase=False,
                helpful_count=r.get("helpful", 0),
            )
            if review.text and len(review.text) > 5:
                reviews.append(review)
        except Exception as e:
            print(f"Review parse error: {e}")
    
    if len(reviews) < 3:
        raise HTTPException(
            status_code=422,
            detail="Yeterli yorum bulunamadı (min. 3 gerekli)",
        )
    
    # Bot tespiti
    bot_percentage, suspicious_count, analyzed_reviews = await analyze_reviews(reviews)
    
    # Duygu analizi
    categories = await analyze_sentiment(analyzed_reviews)
    
    # Risk skoru
    risk_score, risk_level, risk_explanation, trend = calculate_risk(
        bot_percentage, categories, analyzed_reviews, body.platform_rating
    )
    
    # AI özet
    top_complaints = [cat for cat, data in categories.items() if data.negative_ratio > 0.4]
    top_praises = [cat for cat, data in categories.items() if data.positive_ratio > 0.6]
    
    ai_summary_dict = await gemini_service.generate_summary(
        body.product_name,
        body.platform_rating,
        bot_percentage,
        {k: {"positive": v.positive_ratio, "negative": v.negative_ratio} for k, v in categories.items()},
        top_complaints,
        top_praises,
        trend.direction,
    )
    ai_summary = AISummary(**ai_summary_dict)
    
    # Sample reviews
    reliable_negative = sorted(
        [r for r in analyzed_reviews if r.sentiment == "negative"],
        key=lambda x: x.bot_score or 1.0
    )[:3]
    reliable_positive = sorted(
        [r for r in analyzed_reviews if r.sentiment == "positive"],
        key=lambda x: x.bot_score or 0.0
    )[:3]
    
    # CO2 tasarrufu
    co2_saved = calculate_co2_savings(risk_score, len(reviews))
    
    # Sonuç
    dates = [r.date for r in analyzed_reviews]
    
    return AnalysisResult(
        id=str(uuid.uuid4()),
        cached=False,
        product=ProductInfo(
            name=body.product_name,
            image_url=body.product_image,
            price=body.product_price,
            platform="trendyol",
            category="genel",
        ),
        review_stats=ReviewStats(
            total_found=len(body.reviews),
            total_analyzed=len(analyzed_reviews),
            date_range=DateRange(
                oldest=min(dates).date(),
                newest=max(dates).date(),
            ) if dates else None,
        ),
        bot_analysis=BotAnalysis(
            bot_percentage=bot_percentage,
            suspicious_count=suspicious_count,
            confidence="high" if suspicious_count > len(reviews) * 0.3 else "medium",
        ),
        rating_analysis=RatingAnalysis(
            platform_rating=body.platform_rating,
            real_estimated_rating=round(body.platform_rating - (bot_percentage / 100), 1),
            inflation_detected=bot_percentage > 25,
        ),
        categories=categories,
        trend=trend,
        ai_summary=ai_summary,
        risk_score=risk_score,
        risk_level=risk_level,
        risk_explanation=risk_explanation,
        sample_reviews=SampleReviews(
            most_reliable_negative=reliable_negative,
            most_reliable_positive=reliable_positive,
        ),
        sustainability=Sustainability(
            co2_saved_grams=co2_saved,
            message=f"Bu analiz ~{int(co2_saved)}g CO₂ tasarrufu sağlayabilir",
        ),
    )