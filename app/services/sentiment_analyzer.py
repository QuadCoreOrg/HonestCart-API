from collections import defaultdict
from typing import Optional

from app.models.analysis import CategoryAnalysis
from app.models.review import Review
from app.services import gemini_service


class SentimentAnalyzer:
    def __init__(self):
        self.gemini = gemini_service
        self.categories = ["kargo", "kalite", "satıcı", "fiyat", "paketleme", "beden", "teknik"]

    async def analyze(self, reviews: list[Review]) -> dict[str, CategoryAnalysis]:
        """Her yorumu kategori ve duyguya göre etiketler."""
        if not reviews:
            return {}

        # Önce Gemini ile analiz et
        try:
            sentiment_results = await self.gemini.analyze_sentiment([
                {"id": r.id, "text": r.text[:500], "rating": r.rating}
                for r in reviews[:20]  # İlk 20 yorum
            ])
        except:
            sentiment_results = {}

        # Her yorumu güncelle
        for review in reviews:
            review_sentiments = sentiment_results.get(review.id, {})
            review.categories = list(review_sentiments.keys()) if review_sentiments else []

            # Duygu belirleme (rating'a göre)
            if review.rating >= 4:
                review.sentiment = "positive"
            elif review.rating <= 2:
                review.sentiment = "negative"
            else:
                review.sentiment = "neutral"

        # Kategori bazlı agregasyon
        category_data = {cat: {"positive": 0, "negative": 0, "neutral": 0} for cat in self.categories}

        for review in reviews:
            if review.categories:
                for cat in review.categories:
                    if cat in category_data:
                        category_data[cat][review.sentiment] += 1
            else:
                # Kategori yoksa rating'den tahmin et
                if review.rating >= 4:
                    category_data["kalite"]["positive"] += 1
                elif review.rating <= 2:
                    category_data["kalite"]["negative"] += 1

        # CategoryAnalysis oluştur
        result = {}
        for cat, counts in category_data.items():
            total = sum(counts.values())
            if total == 0:
                continue

            positive_ratio = counts["positive"] / total
            negative_ratio = counts["negative"] / total
            neutral_ratio = counts["neutral"] / total

            summary = self._generate_category_summary(cat, positive_ratio, negative_ratio)

            result[cat] = CategoryAnalysis(
                name=cat,
                positive_count=counts["positive"],
                negative_count=counts["negative"],
                neutral_count=counts["neutral"],
                positive_ratio=round(positive_ratio, 2),
                negative_ratio=round(negative_ratio, 2),
                neutral_ratio=round(neutral_ratio, 2),
                sentiment_summary=summary,
            )

        return result

    def _generate_category_summary(self, category: str, positive: float, negative: float) -> str:
        cat_names = {
            "kargo": "Kargo & Teslimat",
            "kalite": "Ürün Kalitesi",
            "satıcı": "Satıcı İletişimi",
            "fiyat": "Fiyat/Performans",
            "paketleme": "Paketleme",
            "beden": "Beden/Uyum",
            "teknik": "Teknik Özellikler",
        }

        name = cat_names.get(category, category)

        if negative > 0.5:
            return f"Kullanıcıların %{int(negative*100)}'ı {category} konusunda memnun değil"
        elif positive > 0.6:
            return f"Kullanıcıların %{int(positive*100)}'ı {category}'den memnun"
        else:
            return f"{name} konusunda karışık görüşler var"


async def analyze_sentiment(reviews: list[Review]) -> dict[str, CategoryAnalysis]:
    analyzer = SentimentAnalyzer()
    return await analyzer.analyze(reviews)