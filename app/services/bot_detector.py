from collections import Counter
from datetime import timedelta
from typing import Optional

from app.models.review import Review
from app.services import gemini_service


class BotDetector:
    def __init__(self):
        self.gemini = gemini_service

    async def analyze(self, reviews: list[Review]) -> tuple[float, int, list[Review]]:
        """
        Returns: (bot_percentage, suspicious_count, reviews_with_scores)
        """
        if not reviews:
            return 0.0, 0, []

        # Kural tabanlı skorlar
        rule_scores = self._rule_based_scores(reviews)

        # Gemini destekli analiz
        try:
            gemini_results = await self.gemini.analyze_bot_scores([
                {"id": r.id, "text": r.text, "rating": r.rating}
                for r in reviews
            ])

            gemini_map = {r["review_id"]: r.get("bot_score", 0.5) for r in gemini_results}
        except:
            gemini_map = {}

        # Kombinasyon: %60 kural, %40 Gemini
        for i, review in enumerate(reviews):
            rule = rule_scores.get(review.id, 0.5)
            gemini = gemini_map.get(review.id, 0.5)

            final_score = (rule * 0.6) + (gemini * 0.4)
            review.bot_score = round(final_score, 2)

        # Toplu istatistik
        suspicious = sum(1 for r in reviews if r.bot_score and r.bot_score > 0.6)
        bot_percentage = (suspicious / len(reviews)) * 100 if reviews else 0

        return round(bot_percentage, 1), suspicious, reviews

    def _rule_based_scores(self, reviews: list[Review]) -> dict[str, float]:
        scores = {}

        # 1. Tarih kümelenmesi (24 saat içinde 10+ yorum = şüpheli)
        date_counts = Counter(r.date.date() for r in reviews)
        max_date_count = max(date_counts.values()) if date_counts else 0
        date_cluster_score = min(max_date_count / 20, 1.0)

        # 2. Yıldız-metin çelişkisi
        negative_words = ["kötü", "berbat", "vasat", "bozuk", "çok", "fena", "pişman", "iade", "beğenmedim"]
        positive_words = ["güzel", "mükemmel", "harika", "tavsiye", "beğendim", "kaliteli"]

        for review in reviews:
            text_lower = review.text.lower()
            has_negative = any(w in text_lower for w in negative_words)
            has_positive = any(w in text_lower for w in positive_words)

            contradiction = 0.0
            if review.rating >= 4 and has_negative:
                contradiction = 0.8
            elif review.rating <= 2 and has_positive:
                contradiction = 0.8
            else:
                contradiction = 0.0

            # 3. Çok kısa yorum + 5 yıldız
            short_score = 0.0
            if len(review.text) < 20 and review.rating == 5:
                short_score = 0.7

            # 4. Genel ifade kalıpları
            generic_patterns = [
                "teşekkürler", "super geldi", "güzel ürün", "tavsiye ederim",
                "çok beğendim", "tüh be", "bir şey yok", "idare eder"
            ]
            generic_score = 0.0
            text_lower = review.text.lower()
            pattern_count = sum(1 for p in generic_patterns if p in text_lower)
            if pattern_count >= 2 and len(review.text) < 50:
                generic_score = 0.6

            # Ortalama
            scores[review.id] = (date_cluster_score * 0.25 + contradiction * 0.2 +
                                 short_score * 0.25 + generic_score * 0.3)

        return scores


async def analyze_reviews(reviews: list[Review]) -> tuple[float, int, list[Review]]:
    detector = BotDetector()
    return await detector.analyze(reviews)