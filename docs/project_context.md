# project_context.md — GerçekSepet Backend

> Bu doküman Claude Code ve AI geliştirme araçları için yazılmıştır.
> Projeye yeni başlarken veya bir göreve başlamadan önce bu dosyayı oku.

---

## Projenin Tek Cümle Özeti

Kullanıcı bir e-ticaret ürün URL'si gönderir; backend yorumları scrape eder, bot tespiti + duygu analizi yapar, Gemini ile özet üretir, 0-100 arası risk skoru döner.

---

## Teknoloji Stack

| Katman        | Teknoloji               | Notlar                          |
| ------------- | ----------------------- | ------------------------------- |
| Framework     | FastAPI (Python 3.11+)  | Async-first                     |
| Scraping      | Firecrawl API           | `firecrawl-py` kütüphanesi      |
| AI            | Google Gemini 1.5 Flash | `google-generativeai`           |
| Veritabanı    | PostgreSQL 16           | asyncpg driver ile              |
| ORM           | SQLAlchemy 2.x (async)  | `AsyncSession` kullan           |
| Cache         | Redis 7                 | `redis.asyncio`                 |
| HTTP Client   | httpx                   | Async, scraping ve dış çağrılar |
| Validasyon    | Pydantic v2             | Model + settings                |
| Linting       | Ruff                    | Hem linter hem formatter        |
| Type Checking | mypy                    | Strict mod                      |
| Container     | Docker Compose          | Dev + prod aynı compose         |
| Deploy        | VPS (Ubuntu)            | Nginx reverse proxy önünde      |

---

## Klasör Yapısı

```
gerçeksepet-api/
│
├── main.py                  # FastAPI app, lifespan, middleware
├── config.py                # Pydantic Settings, tüm env var'lar buradan
│
├── routers/
│   └── analysis.py          # /analyze endpoint'leri
│
├── services/
│   ├── scraper.py           # Firecrawl orchestration, sayfalama
│   ├── bot_detector.py      # Bot tespit (kural tabanlı + Gemini)
│   ├── sentiment_analyzer.py # Kategori bazlı duygu analizi (Gemini)
│   ├── gemini_service.py    # Tüm Gemini çağrıları tek yerden
│   ├── risk_calculator.py   # Risk skoru formülü
│   └── cache_service.py     # Redis cache işlemleri
│
├── models/
│   ├── review.py            # Review Pydantic modeli
│   └── analysis.py          # AnalysisResult + alt modeller
│
├── db/
│   ├── database.py          # AsyncEngine, AsyncSession factory
│   ├── tables.py            # SQLAlchemy tablo tanımları
│   └── crud.py              # DB okuma/yazma fonksiyonları
│
├── scrapers/
│   ├── base.py              # Abstract BaseScraper
│   └── trendyol.py          # Trendyol'a özel URL parse + veri temizleme
│
├── tests/                   # (Şimdilik boş, ilerisi için)
│
├── .env                     # Asla commit'leme
├── .env.example             # Commit'le, değerleri boş bırak
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Servis Sorumlulukları

Her servis **tek bir şey** yapar. Birden fazla servisi doğrudan birbirine bağlama — orkestrasyonu `routers/analysis.py` içinden yap.

### `scraper.py`

- Firecrawl API'ye istek atar
- Trendyol yorum sayfalarını iterate eder (max 4 sayfa / 200 yorum)
- Ham HTML/JSON'ı `scrapers/trendyol.py`'ye parse ettirir
- Dış dünyaya `List[Review]` ve `ProductInfo` döner

### `bot_detector.py`

- `List[Review]` alır
- Kural tabanlı skorları hesaplar (tarih kümelenmesi, metin benzerliği, yıldız-metin çelişkisi)
- Gemini'a toplu skor aldırır (`gemini_service.py` üzerinden)
- Her review'a `bot_score: float (0.0-1.0)` atar
- Toplu `bot_percentage: float` döner

### `sentiment_analyzer.py`

- `List[Review]` alır
- Gemini ile kategori tespiti yapar (kargo, kalite, satıcı, fiyat, paketleme...)
- `Dict[str, CategoryAnalysis]` döner

### `gemini_service.py`

- Tüm Gemini API çağrıları buradan geçer, başka yerden doğrudan çağrılmaz
- Rate limit yönetimi, retry logic burada
- Metodlar: `analyze_bot_scores()`, `analyze_sentiment()`, `generate_summary()`

### `risk_calculator.py`

- Bot skoru + kategori analizi + trend verisi alır
- Ağırlıklı formülle 0-100 arası `risk_score` üretir
- Saf hesaplama, dış servis çağrısı yok

### `cache_service.py`

- URL hash'i key olarak Redis'e yazar/okur
- TTL: 6 saat
- `get_analysis(url_hash)` → `AnalysisResult | None`
- `set_analysis(url_hash, result)` → `None`

---

## Veri Akışı (Request Lifecycle)

```
POST /analyze {"url": "..."}
        │
        ▼
URL validasyonu (Pydantic)
        │
        ▼
cache_service.get() → Cache var mı?
        ├── Evet → Direkt dön (200ms)
        └── Hayır ↓
        │
        ▼
scraper.py → Firecrawl → ProductInfo + List[Review]
        │
        ▼
asyncio.gather() ile paralel:
    ├── bot_detector.analyze(reviews)
    └── sentiment_analyzer.analyze(reviews)
        │
        ▼
asyncio.gather() ile paralel:
    ├── risk_calculator.calculate(bot_results, sentiment_results)
    └── gemini_service.generate_summary(...)
        │
        ▼
AnalysisResult oluştur
        │
        ▼
cache_service.set() → Redis'e yaz
db/crud.py → PostgreSQL'e yaz (istatistik için)
        │
        ▼
Dön (JSON)
```

---

## Async Kuralları

Bu proje **tamamen async**. Şu kurallara uy:

```python
# ✅ DOĞRU
async def get_reviews(url: str) -> list[Review]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    return parse_reviews(response.json())

# ❌ YANLIŞ — blocking çağrı async fonksiyon içinde
async def get_reviews(url: str) -> list[Review]:
    response = requests.get(url)  # requests sync'tir, kullanma
```

**Paralel işlemler için `asyncio.gather()` kullan:**

```python
bot_result, sentiment_result = await asyncio.gather(
    bot_detector.analyze(reviews),
    sentiment_analyzer.analyze(reviews)
)
```

**Sync kütüphane kullanmak zorunda kalırsan** (örn. bir hesaplama kütüphanesi):

```python
import asyncio
result = await asyncio.get_event_loop().run_in_executor(None, sync_function, args)
```

---

## Coding Standards

### Genel

- Python 3.11+ syntax kullan (match/case, `X | None` yerine `Optional[X]` değil)
- Her fonksiyon için type annotation zorunlu (mypy strict)
- Docstring: tek satır yeter, paragraf yazmaya gerek yok
- Magic number kullanma — `config.py`'de sabite çevir

### FastAPI Spesifik

```python
# Router tanımı — her router prefix ve tag alır
router = APIRouter(prefix="/analyze", tags=["analysis"])

# Endpoint — her zaman async def
@router.post("/", response_model=AnalysisResult, status_code=200)
async def analyze_product(
    body: AnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    cache: Redis = Depends(get_redis),
) -> AnalysisResult:
    ...

# HTTP hataları — HTTPException kullan, ham return etme
raise HTTPException(status_code=422, detail="Geçerli bir Trendyol linki girin.")
```

### Pydantic v2

```python
# ✅ v2 syntax
class AnalysisResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    risk_score: int
    bot_percentage: float

# ❌ v1 syntax — kullanma
class Config:
    orm_mode = True
```

### SQLAlchemy Async

```python
# Session her zaman Depends ile inject edilir, elle oluşturma
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Query
result = await session.execute(select(AnalysisCache).where(...))
row = result.scalar_one_or_none()
```

### Error Handling

```python
# Servislerde exception yakala, anlamlı mesajla yeniden fırlat
try:
    result = await firecrawl_client.scrape(url)
except Exception as e:
    logger.error(f"Scraping failed for {url}: {e}")
    raise ScrapingError(f"Ürün bilgilerine ulaşılamadı: {url}") from e

# Router'da custom exception'ları HTTP'ye çevir
@app.exception_handler(ScrapingError)
async def scraping_error_handler(request, exc):
    return JSONResponse(status_code=503, content={"error": "scraping_failed", "message": str(exc)})
```

---

## Ortam Değişkenleri

Tüm config `config.py`'deki `Settings` sınıfından gelir. Hiçbir yerde `os.environ.get()` doğrudan kullanma.

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    firecrawl_api_key: str
    gemini_api_key: str
    cache_ttl_hours: int = 6
    max_reviews_per_analysis: int = 200
    min_reviews_required: int = 10
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = ConfigDict(env_file=".env")

settings = Settings()
```

```env
# .env.example — gerçek değerleri .env'e yaz, .env asla commit'leme
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/gerçeksepet
REDIS_URL=redis://localhost:6379
FIRECRAWL_API_KEY=
GEMINI_API_KEY=
CACHE_TTL_HOURS=6
MAX_REVIEWS_PER_ANALYSIS=200
MIN_REVIEWS_REQUIRED=10
CORS_ORIGINS=["http://localhost:3000"]
```

---

## Docker Compose

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - .:/app # Dev: hot reload için

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: gerçeksepet
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pg_data:
```

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

## Projeyi Ayağa Kaldırma

```bash
# 1. Repo'yu kur
git clone <repo>
cd gerçeksepet-api

# 2. .env oluştur
cp .env.example .env
# .env'i düzenle, API key'leri gir

# 3. Docker ile başlat
docker compose up --build

# 4. API çalıştığını kontrol et
curl http://localhost:8000/health
# → {"status": "ok"}

# 5. Swagger UI
# http://localhost:8000/docs
```

---

## Gemini Entegrasyon Kuralları

- Tüm Gemini çağrıları `services/gemini_service.py` üzerinden geçer
- Her prompt structured output ister (JSON olarak yanıt ver diye belirt)
- Yanıt her zaman `try/except` içinde parse edilir — Gemini bazen format bozabilir
- Rate limit için basit exponential backoff yap (max 3 retry)
- Büyük yorum listelerini **50'lik chunk'lara böl**, tek seferde gönderme

```python
# Prompt şablonu — tüm promptlarda Türkçe yaz, JSON formatı iste
SYSTEM_PROMPT = """
Sen bir e-ticaret yorum analiz uzmanısın.
Senden her zaman sadece geçerli JSON döndürmeni istiyorum.
Markdown, açıklama veya ek metin YAZMA. Sadece JSON.
"""
```

---

## Firecrawl Entegrasyon Notları

- `firecrawl-py` kütüphanesi kullanılır
- Trendyol JavaScript render gerektirir → `formats=["html"]` ile `waitFor` parametresi gerekebilir
- Yorum sayfaları için Trendyol'un iç API endpoint'i doğrudan hedeflenir (HTML parse yerine JSON daha temiz):
  ```
  GET https://public-mdc.trendyol.com/discovery-web-websfxproductrating-santral/api/product-reviews
      ?productId={ID}&page={N}&pageSize=50
  ```
- Bu endpoint public, auth gerektirmiyor — Firecrawl ile direkt fetch et

---

## Bilinen Kısıtlar & Dikkat Noktaları

- **Trendyol sayfa yapısı değişebilir.** Scraper'ı izole tut (`scrapers/trendyol.py`), değişiklik olunca sadece orayı güncelle.
- **Gemini kotası:** Free tier dakikada 15 istek. Geliştirirken dikkat et.
- **Firecrawl free tier:** Aylık 500 sayfa. Demo'da gereksiz istek atma.
- **asyncio.gather içinde exception:** Birisi patlarsa diğerleri iptal olur. `return_exceptions=True` kullanmayı değerlendir.
- **PostgreSQL migration:** Şimdilik Alembic yok, `db/tables.py`'de `Base.metadata.create_all()` ile tablo oluşturuyoruz. Şema değişirse tabloyu drop et, yeniden oluştur (hackathon yeterli).

---

## Endpoints Özeti

| Method | Path            | Açıklama                      |
| ------ | --------------- | ----------------------------- |
| `GET`  | `/health`       | Sağlık kontrolü               |
| `POST` | `/analyze`      | URL analizi başlat            |
| `GET`  | `/analyze/{id}` | Önceki analizi getir          |
| `GET`  | `/stats`        | Platform geneli istatistikler |

Tüm detaylar için: `http://localhost:8000/docs` (Swagger otomatik üretir)

---

_Son güncelleme: Mayıs 2026_
