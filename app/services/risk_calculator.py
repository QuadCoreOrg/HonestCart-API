from datetime import datetime, timedelta
from typing import Optional

from app.models.analysis import CategoryAnalysis, RiskLevel, TrendData
from app.models.review import Review


class RiskCalculator:
    def calculate(
        self,
        bot_percentage: float,
        categories: dict[str, CategoryAnalysis],
        reviews: list[Review],
        platform_rating: float,
    ) -> tuple[int, RiskLevel, str, TrendData]:
        """
        Risk skoru 0-100 arası hesaplar.
        Returns: (risk_score, risk_level, explanation, trend_data)
        """

        # Bileşenler
        bot_component = bot_percentage

        # Kalite negative oranı
        quality_negative = categories.get("kalite", CategoryAnalysis(name="kalite")).negative_ratio
        quality_negative_rate = quality_negative * 100

        # Trend analizi
        trend = self._analyze_trend(reviews)
        recent_complaint_trend = trend.change_percentage if trend.alert else trend.change_percentage * 0.5

        # Yıldız enflasyonu
        real_rating = self._calculate_real_rating(reviews)
        star_inflation = max(0, (platform_rating - real_rating) * 20)  # 0.5 puan fark = 10 puan risk

        # İade şikayetleri
        return_complaints = categories.get("iade", CategoryAnalysis(name="iade")).negative_ratio * 100

        # Ağırlıklı ortalama
        risk_score = (
            bot_component * 0.30 +
            quality_negative_rate * 0.25 +
            recent_complaint_trend * 0.20 +
            star_inflation * 0.15 +
            return_complaints * 0.10
        )

        risk_score = round(min(100, max(0, risk_score)))

        # Seviye belirleme
        risk_level = self._get_risk_level(risk_score)
        explanation = self._generate_explanation(risk_score, bot_percentage, trend, categories)

        return risk_score, risk_level, explanation, trend

    def _calculate_real_rating(self, reviews: list[Review]) -> float:
        if not reviews:
            return 0.0

        # Bot skoru yüksek olanları filtrele
        filtered = [r for r in reviews if not r.bot_score or r.bot_score < 0.6]

        if not filtered:
            filtered = reviews

        return sum(r.rating for r in filtered) / len(filtered)

    def _analyze_trend(self, reviews: list[Review]) -> TrendData:
        if not reviews or len(reviews) < 10:
            return TrendData(
                direction="stable",
                change_percentage=0.0,
                alert=False,
                alert_message="Yeterli veri yok",
            )

        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)

        recent = [r for r in reviews if r.date >= thirty_days_ago]
        previous = [r for r in reviews if sixty_days_ago <= r.date < thirty_days_ago]

        if not recent or not previous:
            return TrendData(
                direction="stable",
                change_percentage=0.0,
                alert=False,
                alert_message="Yeterli veri yok",
            )

        recent_negative_rate = sum(1 for r in recent if r.rating <= 2) / len(recent)
        previous_negative_rate = sum(1 for r in previous if r.rating <= 2) / len(previous)

        change = (recent_negative_rate - previous_negative_rate) * 100

        direction = "increasing" if change > 5 else "decreasing" if change < -5 else "stable"
        alert = change > 15
        alert_message = f"Son 30 günde şikayet oranı %{abs(int(change))} {'arttı' if change > 0 else 'azaldı'}" if alert else ""

        return TrendData(
            direction=direction,
            change_percentage=round(change, 1),
            alert=alert,
            alert_message=alert_message,
        )

    def _get_risk_level(self, score: int) -> RiskLevel:
        if score <= 30:
            return RiskLevel.SAFE
        elif score <= 60:
            return RiskLevel.CAUTION
        elif score <= 80:
            return RiskLevel.RISKY
        else:
            return RiskLevel.VERY_RISKY

    def _generate_explanation(
        self,
        score: int,
        bot_percentage: float,
        trend: TrendData,
        categories: dict[str, CategoryAnalysis],
    ) -> str:
        parts = []

        if bot_percentage > 30:
            parts.append(f"Yorumların %{int(bot_percentage)}'i bot veya manipüle olabilir")

        if categories.get("kalite", CategoryAnalysis(name="kalite")).negative_ratio > 0.5:
            parts.append("Kalite şikayetleri yüksek")

        if trend.alert:
            parts.append(trend.alert_message)

        if score > 60:
            return "Bu ürün riskli. " + ". ".join(parts) if parts else "Satın almadan önce dikkatli değerlendirme önerilir."
        elif score > 30:
            return "Dikkatli olunması önerilir. " + ". ".join(parts) if parts else "Şunlara dikkat edin."
        else:
            return "Bu ürün güvenilir görünüyor."


def calculate_risk(
    bot_percentage: float,
    categories: dict[str, CategoryAnalysis],
    reviews: list[Review],
    platform_rating: float,
) -> tuple[int, RiskLevel, str, TrendData]:
    calculator = RiskCalculator()
    return calculator.calculate(bot_percentage, categories, reviews, platform_rating)