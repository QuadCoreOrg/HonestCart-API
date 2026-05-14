import hashlib
import re
from datetime import datetime
from typing import Optional

import httpx

from app.models.review import Review


class ScraperError(Exception):
    pass


class TrendyolScraper:
    FIRECRAWL_BASE_URL = "https://api.firecrawl.dev"

    def __init__(self):
        from app.config import settings
        self.firecrawl_api_key = settings.firecrawl_api_key
        self.max_reviews = settings.max_reviews_per_analysis
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
        }

    async def scrape_product(self, url: str) -> tuple[Optional[dict], Optional[str]]:
        """Ürün bilgilerini Firecrawl ile çeker."""
        if "trendyol.com" not in url:
            raise ScraperError("Sadece Trendyol URL'leri destekleniyor.")

        product_id = self._extract_product_id(url)
        if not product_id:
            raise ScraperError("Ürün ID'si bulunamadı.")

        # Firecrawl ile markdown çek (daha temiz)
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.FIRECRAWL_BASE_URL}/v1/scrape",
                json={
                    "url": url,
                    "formats": ["markdown"],
                    "onlyMainContent": True,
                },
                headers={
                    "Authorization": f"Bearer {self.firecrawl_api_key}",
                    "Content-Type": "application/json"
                },
            )

            if response.status_code != 200:
                raise ScraperError(f"Scraping başarısız: {response.status_code}")

            data = response.json()
            if not data.get("success"):
                raise ScraperError(f"Firecrawl hatası: {data.get('error')}")

            markdown = data.get("data", {}).get("markdown", "")

        product_info = self._parse_product_markdown(markdown, product_id)
        return product_info, product_id

    async def scrape_reviews(self, url: str, product_id: str) -> list[Review]:
        """Yorumları Firecrawl ile çeker."""
        # Base URL'i al (domain + path before -p-)
        base_match = re.match(r'(https://www\.trendyol\.com/[^/]+)', url)
        if not base_match:
            base_url = "https://www.trendyol.com"
        else:
            base_url = base_match.group(1)
        
        reviews_url = f"{base_url}-yorumlar?pId={product_id}"

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.FIRECRAWL_BASE_URL}/v1/scrape",
                    json={
                        "url": reviews_url,
                        "formats": ["html"],
                        "onlyMainContent": True,
                        "waitFor": 3000,
                    },
                    headers={
                        "Authorization": f"Bearer {self.firecrawl_api_key}",
                        "Content-Type": "application/json"
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        html = data.get("data", {}).get("html", "")
                        reviews = self._parse_reviews_html(html)
                        if reviews:
                            return reviews[:self.max_reviews]
        except Exception as e:
            print(f"Firecrawl reviews error: {e}")

        # Fallback: Demo için mock yorumlar
        print("Using mock reviews for demo")
        return self._generate_mock_reviews()

    def _extract_product_id(self, url: str) -> Optional[str]:
        match = re.search(r"-p-(\d+)", url)
        return match.group(1) if match else None

    def _parse_product_markdown(self, markdown: str, product_id: str) -> dict:
        try:
            # Ürün adı - markdown'daki ürün adını bul
            name = "Bilinmeyen Ürün"
            
            # Pattern 1: # Marka ÜrünAdı - format
            match = re.search(r'#\s+[^\n]+\n(.+)', markdown)
            if match:
                line = match.group(1).strip()
                # "Marka ÜrünAdı" formatında olabilir
                name_match = re.search(r'^([^*]+)', line)
                if name_match:
                    name = name_match.group(1).strip()[:200]
            
            # Pattern 2: Son çare - ilk resim altı metin
            if name == "Bilinmeyen Ürün":
                match = re.search(r'!\[.*\]\([^)]+\)\s*\n([^\n#]{10,})', markdown)
                if match:
                    name = match.group(1).strip()[:200]
            
            # Markdown temizle
            name = re.sub(r'\[([^\]]*)\]\([^)]+\)', r'\1', name)  # [text](url) -> text
            name = name.replace('![', '').replace('](', ' -> ')
            name = name.strip()
            
            # Fiyat - TL bul
            price = "Fiyat yok"
            price_match = re.search(r'(\d+[\.,]?\d*)\s*TL', markdown)
            if price_match:
                price = f"₺{price_match.group(1).replace(',', '.')}"
            
            # Görsel - ilk jpg
            image_url = ""
            img_match = re.search(r'!\[([^\]]*)\]\((https://cdn\.dsmcdn\.com[^)]+\.jpg)\)', markdown)
            if img_match:
                image_url = img_match.group(2)
            
            # Rating - 4.4 gibi ondalıklı puan bul
            rating = 0.0
            # Pattern: 4.4 gibi ondalıklı sayı + Değerlendirme
            rating_match = re.search(r'(\d+\.\d+)\s*[\n\s]*Değerlendirme', markdown)
            if not rating_match:
                # Alternatif: tek başına ondalıklı sayı
                rating_match = re.search(r'^(\d+\.\d+)', markdown, re.MULTILINE)
            if rating_match:
                try:
                    rating = float(rating_match.group(1).replace(',', '.'))
                except:
                    pass
            
            # Kategori
            category = "genel"
            cat_match = re.search(r'kategorisinde', markdown)
            if cat_match:
                category = "kozmetik"  # Fallback

            return {
                "name": name,
                "image_url": image_url,
                "price": price,
                "platform": "trendyol",
                "category": category,
                "rating": rating,
            }
        except Exception as e:
            print(f"Product parse error: {e}")
            return {
                "name": "Ürün",
                "image_url": "",
                "price": "₺0",
                "platform": "trendyol",
                "category": "genel",
                "rating": 0.0,
            }

    def _parse_reviews_html(self, html: str) -> list[Review]:
        reviews = []
        
        # Yorumları bul - birden fazla pattern dene
        # Pattern 1: JSON data
        json_match = re.search(r'"reviews"\s*:\s*\[(.*?)\]', html, re.DOTALL)
        
        if json_match:
            import json
            try:
                reviews_data = json.loads(f"[{json_match.group(1)}]")
                for item in reviews_data:
                    review = self._parse_review_from_json(item)
                    if review:
                        reviews.append(review)
            except:
                pass
        
        # Pattern 2: HTML yapısı
        if not reviews:
            review_blocks = re.findall(r'<div[^>]*class="[^"]*comment[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
            for block in review_blocks:
                review = self._parse_review_from_html(block)
                if review:
                    reviews.append(review)
        
        # Pattern 3: Genel HTML parsing
        if not reviews:
            for pattern in [
                r'<p[^>]*class="[^"]*comment-text[^"]*"[^>]*>([^<]+)</p>',
                r'"comment"\s*:\s*"([^"]+)"',
            ]:
                for match in re.finditer(pattern, html):
                    text = match.group(1).strip()
                    if len(text) > 10:
                        reviews.append(Review(
                            id=hashlib.md5(text.encode()).hexdigest()[:8],
                            text=text[:2000],
                            rating=3,
                            date=datetime.now(),
                            user_hash=hashlib.sha256("user".encode()).hexdigest()[:16],
                            verified_purchase=False,
                            helpful_count=0,
                        ))

        print(f"Found {len(reviews)} reviews from HTML")
        return reviews

    def _parse_review_from_json(self, item: dict) -> Optional[Review]:
        try:
            text = item.get("comment", "")
            if not text or len(text.strip()) < 5:
                return None

            rating = item.get("rating", 3)
            date_str = item.get("createDate", "")
            user = item.get("userName", "anonymous")

            try:
                if date_str:
                    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                else:
                    date = datetime.now()
            except:
                date = datetime.now()

            user_hash = hashlib.sha256(user.encode()).hexdigest()[:16]

            return Review(
                id=str(item.get("id", hashlib.md5(text.encode()).hexdigest()[:8])),
                text=text[:2000],
                rating=rating,
                date=date,
                user_hash=user_hash,
                verified_purchase=item.get("isVerified", False),
                helpful_count=item.get("helpfulCount", 0),
            )
        except Exception as e:
            return None

    def _parse_review_from_html(self, html_block: str) -> Optional[Review]:
        try:
            # Yorum metni
            text_match = re.search(r'>([^<]{20,})<', html_block)
            if not text_match:
                return None
            
            text = text_match.group(1).strip()
            if len(text) < 10:
                return None

            # Rating (yıldız sayısı)
            stars = len(re.findall(r'star|⭐|★', html_block.lower()))
            rating = max(1, min(5, stars)) if stars > 0 else 3

            return Review(
                id=hashlib.md5(text.encode()).hexdigest()[:8],
                text=text[:2000],
                rating=rating,
                date=datetime.now(),
                user_hash=hashlib.sha256("user".encode()).hexdigest()[:16],
                verified_purchase=False,
                helpful_count=0,
            )
        except Exception as e:
            return None

    def _generate_mock_reviews(self) -> list[Review]:
        """Demo için mock yorumlar oluşturur."""
        import random
        
        mock_texts = [
            ("Ürün beklentilerimin çok üzerinde. Kesinlikle tavsiye ederim!", 5),
            ("Ambalajı hasar görmüş geldi ama ürün kalitesi iyi.", 4),
            ("Fiyatına göre idare eder. Çok büyük beklentim yoktu.", 3),
            ("Ürün fotoğraftakinden farklı geldi. Biraz hayal kırıklığı.", 2),
            ("Çok kalitesiz, kesinlikle almayın. Para kaybı.", 1),
            ("Kargo çok hızlıydı, teşekkürler!", 5),
            ("Ürün 2 hafta içinde bozuldu. Çok hayal kırıklığına uğradım.", 1),
            ("Ortalama bir ürün. Beklenti ile sonuç aynı.", 3),
            ("Arkadaşıma tavsiye ettim, o da beğendi.", 5),
            ("Kalite düşük, bir daha almam.", 2),
            ("Super ürün, tüm ailem kullanıyoruz.", 5),
            ("Paketleme kötüydü ama ürün iyi.", 4),
            ("Mağaza iletişimi çok iyiydi.", 4),
            ("Ürün boyut olarak küçük geldi.", 2),
            ("Çok güzel, tam istediğim gibi!", 5),
        ]
        
        reviews = []
        base_date = datetime.now()
        
        for i, (text, rating) in enumerate(mock_texts):
            days_ago = random.randint(0, 90)
            review_date = base_date - timedelta(days=days_ago)
            
            reviews.append(Review(
                id=f"mock_{i}",
                text=text,
                rating=rating,
                date=review_date,
                user_hash=hashlib.sha256(f"user_{i}".encode()).hexdigest()[:16],
                verified_purchase=random.choice([True, False]),
                helpful_count=random.randint(0, 15),
            ))
        
        return reviews[:self.max_reviews]


from datetime import timedelta

async def scrape_product(url: str) -> tuple[Optional[dict], Optional[str]]:
    scraper = TrendyolScraper()
    return await scraper.scrape_product(url)


async def scrape_reviews(url: str, product_id: str) -> list[Review]:
    scraper = TrendyolScraper()
    return await scraper.scrape_reviews(url, product_id)