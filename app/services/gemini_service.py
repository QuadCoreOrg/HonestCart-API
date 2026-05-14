import json
from typing import Any

from google import genai
from google.genai import types

from app.config import settings


class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = "gemini-2.0-flash"

    async def analyze_bot_scores(self, reviews: list[dict]) -> list[dict]:
        """50 yorumluk batch'ler halinde bot skoru analizi yapar."""
        results = []

        for i in range(0, len(reviews), 50):
            batch = reviews[i : i + 50]
            result = await self._analyze_batch(batch)
            results.extend(result)

        return results

    async def _analyze_batch(self, reviews: list[dict]) -> list[dict]:
        prompt = f"""
Sen bir e-ticaret yorum bot tespit uzmanısın.
Aşağıdaki yorumları incele ve her yorum için:
1. Bot olma olasılığı (0.0-1.0 arası)
2. Şüpheli ise sebebi

Kriterler: doğallık, özgünlük, bağlamsal uygunluk, dil kalitesi.
Türkçe yorumlar için Türkçe doğallığını değerlendir.

Yorumlar (JSON array):
{json.dumps(reviews, ensure_ascii=False, indent=2)}

Yanıtı sadece JSON olarak ver:
[{{"review_id": "x", "bot_score": 0.X, "reason": "..."}}]

Markdown veya açıklama YAZMA. Sadece JSON.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini bot analysis error: {e}")
            return [{"review_id": r.get("id", str(i)), "bot_score": 0.5, "reason": "Analysis failed"} for i, r in enumerate(reviews)]

    async def analyze_sentiment(self, reviews: list[dict]) -> dict[str, dict]:
        """Her yorumu kategori ve duyguya göre etiketler."""
        prompt = f"""
Sen bir e-ticaret yorum analiz uzmanısın.
Aşağıdaki yorumları analiz et ve her yorum için:
1. Hangi kategorileri kapsıyor? (kargo, kalite, satıcı, fiyat, paketleme, beden, teknik)
2. Her kategori için duygu (positive/negative/neutral)

Yorumlar:
{json.dumps(reviews[:20], ensure_ascii=False, indent=2)}

Yanıtı sadece JSON olarak ver. Örnek format: {{"review_id": {{"kargo": "positive", "kalite": "negative"}}}}
Markdown veya açıklama YAZMA.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini sentiment analysis error: {e}")
            return {}

    async def generate_summary(
        self,
        product_name: str,
        platform_rating: float,
        bot_percentage: float,
        categories: dict[str, dict],
        top_complaints: list[str],
        top_praises: list[str],
        trend_direction: str,
    ) -> dict:
        """AI destekli özet üretir - önce Gemini, yoksa template fallback."""
        
        # Önce Gemini dene
        try:
            prompt = f"""
Sen bir tüketici hakları uzmanısın.
Aşağıdaki e-ticaret ürün analiz verilerini kullanarak Türkçe, açık ve pratik bir özet yaz.

Veriler:
- Ürün: {product_name}
- Platform puanı: {platform_rating}
- Bot oranı: {bot_percentage}%
- Kategori analizi: {json.dumps(categories, ensure_ascii=False)}
- En sık şikayetler: {json.dumps(top_complaints, ensure_ascii=False)}
- En sık övgüler: {json.dumps(top_praises, ensure_ascii=False)}
- Trend: {trend_direction}

Format:
1. Tek cümlelik genel değerlendirme
2. "Kullanıcılar bundan şikayet ediyor:" (3-5 madde)
3. "Kullanıcılar bunu seviyor:" (2-3 madde)
4. "Dikkat et:" (1-2 kritik uyarı)

Abartma, tarafsız ol. Maksimum 150 kelime.

Yanıtı sadece JSON olarak ver:
{{"overall": "...", "complaints": [...], "praises": [...], "warnings": [...]}}
"""
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini summary error: {e}")
        
        # Fallback: Template-based özet
        return self._generate_template_summary(
            product_name, platform_rating, bot_percentage, 
            categories, top_complaints, top_praises, trend_direction
        )
    
    def _generate_template_summary(
        self,
        product_name: str,
        platform_rating: float,
        bot_percentage: float,
        categories: dict[str, dict],
        top_complaints: list[str],
        top_praises: list[str],
        trend_direction: str,
    ) -> dict:
        """Template-based fallback özet."""
        
        # Genel değerlendirme
        if platform_rating >= 4.5:
            overall = f"{product_name}, yüksek puanlı ve genel olarak beğenilen bir ürün."
        elif platform_rating >= 4.0:
            overall = f"{product_name}, ortalama üstü performans gösteren bir ürün."
        elif platform_rating >= 3.5:
            overall = f"{product_name}, karışık yorumlara sahip bir ürün."
        else:
            overall = f"{product_name}, düşük puanlı ve dikkatli değerlendirme gereken bir ürün."
        
        # Şikayetler
        complaints = []
        if bot_percentage > 30:
            complaints.append(f"Yorumların %{int(bot_percentage)}'i şüpheli olarak değerlendirildi")
        
        for cat, data in categories.items():
            if data.get("negative", 0) > 0.4:
                cat_names = {
                    "kalite": "kalite sorunları",
                    "kargo": "kargo gecikmeleri ve hasar",
                    "fiyat": "fiyat-performans dengesizliği",
                    "paketleme": "paketleme problemleri",
                    "beden": "beden uyumsuzluğu",
                }
                complaints.append(cat_names.get(cat, f"{cat} ile ilgili sorunlar"))
        
        if trend_direction == "increasing":
            complaints.append("Son dönemde şikayetler artış eğiliminde")
        
        # Övgüler
        praises = []
        for cat, data in categories.items():
            if data.get("positive", 0) > 0.6:
                cat_names = {
                    "kalite": "Kalitesi beğeniliyor",
                    "kargo": "Kargo hızı ve güvenilirliği",
                    "fiyat": "Fiyat-performans oranı",
                    "paketleme": "Paketleme kalitesi",
                }
                praises.append(cat_names.get(cat, f"{cat} konusunda memnuniyet"))
        
        if not praises and platform_rating >= 4.0:
            praises.append("Genel olarak ürün beğeniliyor")
        
        # Uyarılar
        warnings = []
        if bot_percentage > 40:
            warnings.append("Yorumların güvenilirliği düşük")
        if trend_direction == "increasing":
            warnings.append("Son dönemde şikayetler artıyor")
        if platform_rating < 3.5:
            warnings.append("Puan düşük, detaylı inceleme önerilir")
        
        return {
            "overall": overall,
            "complaints": complaints[:5],
            "praises": praises[:3],
            "warnings": warnings[:2],
        }


gemini_service = GeminiService()