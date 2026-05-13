# GerçekSepet — Product Requirements Document (PRD)

**Versiyon:** 1.0  
**Tarih:** Mayıs 2026  
**Hazırlayan:** Ürün Ekibi  
**Durum:** Hackathon Prototipi (v0.1) → Üretim (v1.0)

---

## İÇİNDEKİLER

1. [Executive Summary](#1-executive-summary)
2. [Problem Tanımı](#2-problem-tanımı)
3. [Çözüm & Vizyon](#3-çözüm--vizyon)
4. [Hedef Kitle](#4-hedef-kitle)
5. [Sürdürülebilirlik Bağlantısı](#5-sürdürülebilirlik-bağlantısı)
6. [Özellikler & Gereksinimler](#6-özellikler--gereksinimler)
7. [Kullanıcı Akışları](#7-kullanıcı-akışları)
8. [Teknik Mimari](#8-teknik-mimari)
9. [AI & Analiz Motoru](#9-ai--analiz-motoru)
10. [Veri Modeli](#10-veri-modeli)
11. [API Kontratları](#11-api-kontratları)
12. [UI/UX Gereksinimleri](#12-uiux-gereksinimleri)
13. [Scraping Stratejisi](#13-scraping-stratejisi)
14. [Chrome Extension](#14-chrome-extension)
15. [Güvenlik & Gizlilik](#15-güvenlik--gizlilik)
16. [Performans Gereksinimleri](#16-performans-gereksinimleri)
17. [Ölçme & Başarı Kriterleri](#17-ölçme--başarı-kriterleri)
18. [Roadmap](#18-roadmap)
19. [Riskler & Azaltma Stratejileri](#19-riskler--azaltma-stratejileri)
20. [Hackathon Demo Planı](#20-hackathon-demo-planı)

---

## 1. Executive Summary

**GerçekSepet**, kullanıcıların Trendyol, Amazon ve Hepsiburada gibi e-ticaret platformlarındaki ürün yorumlarını yapay zeka ile analiz ederek satın alma kararlarını daha bilinçli almalarını sağlayan bir web uygulaması ve Chrome uzantısıdır.

Kullanıcı yalnızca bir ürün bağlantısı yapıştırır; sistem yorumları toplar, bot olma ihtimalini hesaplar, duygu analizini çıkarır ve somut bir **Risk Skoru** üretir. Nihai hedef: e-ticaretteki bilgi asimetrisini ortadan kaldırmak ve insanları yanlış satın alımlardan korumak.

**Hackathon Bağlamı:** "Sürdürülebilir Enerji ile Geleceği Kodla" temalı 48 saatlik yarışma için geliştirilmektedir. Sürdürülebilirlik bağlantısı: yanlış satın alımların önlenmesi → iade kaynaklı kargo emisyonlarının azaltılması → karbon ayak izinin düşürülmesi.

---

## 2. Problem Tanımı

### 2.1 Pazar Gerçekliği

Türkiye e-ticaret pazarı 2025 itibarıyla 850 milyar TL'yi aştı. Trendyol günlük 3 milyonun üzerinde sipariş işliyor. Bu büyüme beraberinde ciddi bir güven krizini getirdi.

### 2.2 Kullanıcı Acı Noktaları

| Sorun                               | Etki                                     | Sıklık      |
| ----------------------------------- | ---------------------------------------- | ----------- |
| Sahte/bot yorumlar                  | Yanlış satın alma kararı                 | Çok yaygın  |
| Yorum enflasyonu (herkese 5 yıldız) | Gerçek kalite gizleniyor                 | Yaygın      |
| Satıcı manipülasyonu                | Sistematik aldatma                       | Artan trend |
| Ürün özellikleri yanıltıcı          | Boyut, renk, malzeme tutarsızlığı        | Yaygın      |
| Geç şikayet görünürlüğü             | Sorunlar yorumlarda gömülü kalıyor       | Yaygın      |
| Dil bariyeri                        | Yabancı ürünlerin yorumları anlaşılmıyor | Orta düzey  |

### 2.3 Mevcut Çözümlerin Yetersizliği

- **Trendyol/Amazon'un kendi filtreleri:** Platform çıkarlarıyla çakışıyor; satıcı ödemesi yapıyorsa görmezden geliniyor.
- **Fakespot (Mozilla):** Sadece Amazon, yalnızca İngilizce, Türkiye pazarı yok.
- **ReviewMeta:** Benzer kısıt, Türkçe destek yok.
- **Manuel okuma:** 500+ yorumu okumak için kullanıcının zamanı ve motivasyonu yok.

### 2.4 Problemin Büyüklüğü

- Türkiye'de e-ticaret iade oranı ortalama %15-25
- Her iadenin kargo + depo maliyeti: ~50-150 TL
- Bu maliyetin önemli bir kısmı yanlış beklenti yönetiminden kaynaklanıyor
- Sürdürülebilirlik açısından: her gereksiz kargo teslimatı ortalama 0.5-2 kg CO₂ emisyonu

---

## 3. Çözüm & Vizyon

### 3.1 Ürün Vizyon Cümlesi

> "Herhangi bir ürün bağlantısını yapıştır, 30 saniye içinde o ürün hakkındaki gerçeği öğren."

### 3.2 Temel Değer Önermesi

GerçekSepet, yorumları sen okumak zorunda kalmadan okur. Botları filtreler, şikayetleri yüzeye çıkarır, tekrar eden kalıpları yakalar ve sana güvenilir bir özet sunar. Satın almadan önce gerçeği görürsün.

### 3.3 Ürün Kapsamı (v0.1 Hackathon)

- **Web Uygulaması:** Next.js, URL yapıştır → analiz al
- **Desteklenen Platform:** Trendyol (öncelikli)
- **Analiz Bileşenleri:** Bot skoru, duygu analizi, kategori bazlı şikayet özeti, risk skoru
- **AI:** Google Gemini API

### 3.4 Ürün Kapsamı (v1.0 Üretim)

- Web + Chrome Extension
- Trendyol + Amazon TR + Hepsiburada
- Kullanıcı hesabı, analiz geçmişi, favoriler
- Karşılaştırmalı ürün analizi
- E-posta/push bildirimleri (fiyat düşüşü + güvenilirlik uyarısı)

---

## 4. Hedef Kitle

### 4.1 Birincil Persona — "Şüpheci Alışverişçi Selin"

- **Yaş:** 24-38
- **Davranış:** Satın almadan önce en az 10 dakika araştırıyor, yorumları tek tek okuyor, sosyal medyada "bu ürünü alan var mı?" diye soruyor
- **Acı noktası:** Yorumlara güvenmek istiyor ama manipüle edildiğini hissediyor
- **Motivasyon:** Yanlış ürün alıp para ve zaman kaybetmek istemiyor
- **Teknoloji kullanımı:** Smartphone + laptop, Chrome kullanıcısı

### 4.2 İkincil Persona — "E-Ticarete Yeni Başlayan Mehmet Amca"

- **Yaş:** 45-60
- **Davranış:** E-ticareti az kullanan, yorumları nasıl değerlendireceğini bilmiyor
- **Acı noktası:** Kolayca aldatılıyor, iade süreçleriyle uğraşamıyor
- **Motivasyon:** Güvenli alışveriş yapmak
- **Teknoloji kullanımı:** Telefon öncelikli

### 4.3 Üçüncül Persona — "Araştırmacı Cem"

- **Yaş:** 22-30
- **Davranış:** Pahalı bir ürün almadan önce kapsamlı araştırma yapıyor (elektronik, beyaz eşya)
- **Acı noktası:** Birden fazla platformda aynı ürünün yorumlarını karşılaştırma zorluğu
- **Motivasyon:** En iyi değer/para oranını bulmak

---

## 5. Sürdürülebilirlik Bağlantısı

### 5.1 Doğrudan Etki Zinciri

```
Yanlış satın alma önlenir
        ↓
İade gerçekleşmez
        ↓
Kargo aracı çıkmaz (teslimat + iade = 2 sefer)
        ↓
CO₂ emisyonu azalır
        ↓
Depo geri dönüş işlemi yapılmaz
        ↓
Ürün imha/bozulma azalır
```

### 5.2 Somutlaştırılmış Etki

- Ortalama kargo teslimatı: ~1.2 kg CO₂ (son mil)
- İade dahil: ~2.4 kg CO₂ (çift yön)
- GerçekSepet ile önlenen her yanlış alımda: ~2.4 kg CO₂ tasarrufu
- 100.000 analiz/ay × %10 iade önleme = 24 ton CO₂/ay tasarrufu

### 5.3 Hackathon Sunum Çerçevesi

"GerçekSepet yalnızca paranızı korumaz — gezegenimizi de korur. Her önlenen yanlış satın alım, gereksiz bir kargo seferinin önüne geçer. Biz bunu ölçüyor ve kullanıcılara gösteriyoruz."

UI'da her analizin altında: **"Bu analiz tahminen X gram CO₂ tasarrufuna katkı sağladı"** bilgisi gösterilecek.

---

## 6. Özellikler & Gereksinimler

### 6.1 Temel Özellikler (Must Have — v0.1)

#### F-01: URL Analiz Girişi

- Kullanıcı Trendyol ürün URL'sini bir input alanına yapıştırır
- URL validasyonu (Trendyol domain kontrolü)
- Analiz butonu
- Yükleme durumu göstergesi (animasyonlu, süreç adımlarıyla)

#### F-02: Yorum Toplama (Scraping)

- Verilen URL'den ürün yorumlarını çekme
- Minimum 50, ideal 200+ yorum (mevcut sayfa sayısına göre)
- Yorum metni, tarihi, yıldız puanı, kullanıcı adı verilerini alma
- Çekilen yorum sayısını kullanıcıya gösterme

#### F-03: Bot/Fake Yorum Tespiti

- Her yorum için bot olasılık skoru hesaplama (0-100)
- Toplu bot skoru: "Yorumların %X'i bot/manipüle olabilir"
- Tespit sinyalleri (detaylar §9'da): dil tekrarı, tarih kümelenmesi, genel ifade kalıpları, yıldız-metin tutarsızlığı

#### F-04: Duygu Analizi

- Yorumların genel tonu: Pozitif / Nötr / Negatif dağılımı
- Kategori bazlı analiz (ürüne göre dinamik):
  - Kargo & Teslimat
  - Ürün Kalitesi
  - Satıcı İletişimi
  - Fiyat/Performans
  - Paketleme
  - (Ürüne özel: Beden, Batarya, Renk Uyumu, vb.)

#### F-05: AI Yorum Özeti

- Gemini ile üretilen doğal dil özeti
- "Kullanıcılar genel olarak şunlardan şikayet ediyor: ..."
- "Öne çıkan övgüler: ..."
- "Dikkat edilmesi gereken: ..."
- Maksimum 5-7 madde, net ve pratik

#### F-06: Risk Skoru

- 0-100 arası tek bir risk puanı
- Görsel gösterim: renk kodlu (0-30 Güvenli, 31-60 Dikkatli, 61-100 Riskli)
- Risk bileşenlerinin ağırlıklı ortalaması (§9.3'te tanımlı)
- Skoru açıklayan kısa bir paragraf

#### F-07: Zaman Bazlı Analiz

- Son 1 ay / 3 ay / tüm zamanlar filtresi
- Şikayet trendi grafiği (artan mı, azalan mı?)
- "Son 30 günde iade şikayeti artmış" gibi özel uyarılar

#### F-08: Karbon Etkisi Göstergesi

- Her analiz sayfasının altında: "Bu analiz X gram CO₂ tasarrufuna potansiyel katkı sağlayabilir"
- Toplam platform istatistiği: "GerçekSepet kullanıcıları bu ay X ton CO₂ tasarrufu sağladı"

### 6.2 Önemli Özellikler (Should Have — v0.1'de varsa iyi)

#### F-09: Yorum Örnekleri

- "En dikkat çekici negatif yorumlar" — 3-5 örnek
- "En güvenilir pozitif yorumlar" — 3-5 örnek (bot skoru düşük olanlar)
- Tarih, yıldız ve güvenilirlik göstergesiyle birlikte

#### F-10: Ürün Özeti Kartı

- Ürün adı, görseli, fiyatı (scraping'den)
- Ortalama puan vs. "gerçek kullanıcı puanı" karşılaştırması
- Kaç yorum analiz edildi

#### F-11: Paylaşım Özelliği

- "Bu analizi paylaş" butonu
- Analiz sayfasına kalıcı link (slug bazlı)
- WhatsApp / Twitter / kopyala paylaşım seçenekleri

### 6.3 Gelecek Özellikler (Won't Have — v0.1, v1.0'da hedef)

#### F-12: Kullanıcı Hesabı

- Kayıt/giriş
- Analiz geçmişi
- Favori ürünler takibi

#### F-13: Fiyat-Güvenilirlik Takibi

- Ürün fiyatı ve risk skoru zaman içinde izleme
- "Risk düştü, alabilirsin" bildirimi

#### F-14: Çoklu Platform Desteği

- Amazon TR scraping
- Hepsiburada scraping
- N11 scraping

#### F-15: Karşılaştırma Modu

- İki ürünü yan yana analiz etme
- "Hangisini almalıyım?" önerisi

#### F-16: Mobil Uygulama

- React Native (Expo)
- Deep link ile platform uygulamalarından paylaşım

---

## 7. Kullanıcı Akışları

### 7.1 Ana Akış — Web Uygulaması

```
[KULLANICI]
    │
    ▼
Landing Page — Hero bölümü
"Satın Almadan Önce Gerçeği Gör"
[URL input alanı]
    │
    │ URL yapıştır + "Analiz Et" tıkla
    ▼
URL Validasyonu
    ├─ Geçersiz URL → Hata mesajı göster, input'u temizle
    └─ Geçerli URL → Analiz sürecini başlat
    │
    ▼
Yükleme Ekranı (15-30 saniye)
Animasyonlu adımlar:
  ✓ "Ürün bilgileri alınıyor..."
  ✓ "Yorumlar toplanıyor (X yorum bulundu)..."
  ✓ "Bot analizi yapılıyor..."
  ✓ "AI yorumları değerlendiriyor..."
  ✓ "Risk skoru hesaplanıyor..."
    │
    ▼
Analiz Sonuç Sayfası
┌─────────────────────────────────────┐
│ [Ürün Kartı: Görsel + İsim + Fiyat] │
│ Platform Puanı: ⭐ 4.6 (1.243 yorum) │
│ GerçekSepet Puanı: ⭐ 3.1           │
├─────────────────────────────────────┤
│ RİSK SKORU: 67 / 100               │
│ 🟠 DİKKATLİ OL                      │
├─────────────────────────────────────┤
│ 🤖 Bot Analizi: %38 şüpheli yorum  │
│ 😤 En Sık Şikayet: Kalite, Beden    │
│ 📦 Kargo: Genel olarak olumlu       │
│ 📉 Son 30 gün: Şikayet artışı var  │
├─────────────────────────────────────┤
│ AI ÖZETİ                            │
│ "Bu üründe..."                      │
├─────────────────────────────────────┤
│ DİKKAT ÇEKİCİ YORUMLAR             │
│ [Yorum örnekleri]                   │
├─────────────────────────────────────┤
│ 🌱 Bu analiz ~120g CO₂ tasarrufu   │
│    sağlayabilir                     │
├─────────────────────────────────────┤
│ [Paylaş] [Başka Ürün Analiz Et]    │
└─────────────────────────────────────┘
    │
    ├─ "Başka Ürün Analiz Et" → Ana sayfaya dön
    └─ "Paylaş" → Paylaşım menüsü
```

### 7.2 Hata Akışları

| Hata Durumu        | Kullanıcı Mesajı                                                 | Aksiyon                   |
| ------------------ | ---------------------------------------------------------------- | ------------------------- |
| Geçersiz URL       | "Geçerli bir Trendyol ürün linki girin."                         | Input odaklanır           |
| Scraping başarısız | "Ürün bilgilerine şu an ulaşamadık. Tekrar deneyin."             | Retry butonu              |
| Yorum bulunamadı   | "Bu ürün için yeterli yorum bulunamadı (min. 10 yorum gerekli)." | Açıklama                  |
| AI API hatası      | "Analiz şu an yapılamıyor. Lütfen bekleyin."                     | Otomatik retry + hata log |
| Timeout (>60sn)    | "Analiz beklenenden uzun sürdü. Ürün karmaşık olabilir."         | Kısmi sonuç göster        |

### 7.3 Chrome Extension Akışı (v1.0)

```
Kullanıcı Trendyol ürün sayfasındayken
    │
    ▼
Extension ikonuna tıklar (toolbar'da)
    │
    ▼
Popup açılır:
"Bu ürünü analiz et?" [Evet / Hayır]
    │
    │ Evet
    ▼
Extension DOM'dan yorumları okur
(Sayfa scraping yerine — TOS uyumlu)
    │
    ▼
Backend'e gönderir, analiz başlar
    │
    ▼
Popup'ta mini sonuç kartı:
Risk: 🟠 67 — Dikkatli Ol
Bot: %38 şüpheli
[Detaylı Görüntüle →]
    │
    └─ "Detaylı Görüntüle" → GerçekSepet web sayfasında tam analiz
```

---

## 8. Teknik Mimari

### 8.1 Sistem Genel Görünümü

```
┌────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│  Next.js 14 (App Router)                                   │
│  React + TailwindCSS + Framer Motion                       │
│  Recharts (grafik)                                          │
└───────────────────┬────────────────────────────────────────┘
                    │ HTTPS REST API
┌───────────────────▼────────────────────────────────────────┐
│                        BACKEND                              │
│  FastAPI (Python 3.11+)                                    │
│  Pydantic v2 (veri validasyonu)                            │
│  Uvicorn + Gunicorn                                         │
└─────┬───────────────────┬──────────────────────────────────┘
      │                   │
┌─────▼──────┐    ┌───────▼──────────────────────────────────┐
│  Scraping  │    │              İŞLEM KUYRUĞU                │
│  Layer     │    │  Celery + Redis (opsiyonel v0.1)          │
│ ScraperAPI │    └──────────────────────────────────────────┘
│ /Firecrawl │
└─────┬──────┘    ┌──────────────────────────────────────────┐
      │           │              AI LAYER                     │
      │           │  Google Gemini 1.5 Flash API             │
      │           └──────────────────────────────────────────┘
┌─────▼──────────────────────────────────────────────────────┐
│                     VERİ KATMANI                            │
│  PostgreSQL (analiz cache, ürün meta)                      │
│  Redis (oturum, rate limit, kısa cache)                    │
└────────────────────────────────────────────────────────────┘
```

### 8.2 Klasör Yapısı

#### Frontend (Next.js)

```
gerçeksepet-web/
├── app/
│   ├── page.tsx                    # Landing / URL giriş
│   ├── analyze/
│   │   └── [analysisId]/
│   │       └── page.tsx            # Analiz sonuç sayfası
│   ├── layout.tsx
│   └── globals.css
├── components/
│   ├── ui/                         # Shadcn/ui bileşenleri
│   ├── RiskScoreGauge.tsx          # Risk skoru göstergesi
│   ├── BotAnalysisBar.tsx          # Bot tespit görselleştirmesi
│   ├── SentimentChart.tsx          # Duygu dağılım grafiği
│   ├── ReviewCard.tsx              # Tek yorum kartı
│   ├── CategoryBreakdown.tsx       # Kategori bazlı analiz
│   ├── TrendChart.tsx              # Zaman bazlı şikayet trendi
│   ├── CarbonBadge.tsx             # CO₂ tasarruf rozeti
│   └── LoadingSteps.tsx            # Animasyonlu yükleme
├── lib/
│   ├── api.ts                      # Backend API client
│   └── utils.ts
└── types/
    └── analysis.ts                 # TypeScript tipleri
```

#### Backend (FastAPI)

```
gerçeksepet-api/
├── main.py                         # FastAPI app entry
├── routers/
│   └── analysis.py                 # /analyze endpoint'leri
├── services/
│   ├── scraper.py                  # Scraping orchestration
│   ├── bot_detector.py             # Bot tespit algoritması
│   ├── sentiment_analyzer.py       # Duygu analizi
│   ├── gemini_service.py           # Gemini API entegrasyonu
│   └── risk_calculator.py          # Risk skoru hesaplama
├── models/
│   ├── review.py                   # Review Pydantic modeli
│   └── analysis.py                 # AnalysisResult modeli
├── db/
│   ├── database.py                 # DB bağlantısı
│   └── crud.py                     # DB işlemleri
├── scrapers/
│   ├── base_scraper.py             # Abstract scraper
│   └── trendyol_scraper.py         # Trendyol'a özel scraper
└── config.py                       # Ayarlar (env vars)
```

### 8.3 Teknoloji Stack Detayı

| Katman             | Teknoloji        | Versiyon          | Neden                                    |
| ------------------ | ---------------- | ----------------- | ---------------------------------------- |
| Frontend framework | Next.js          | 14.x (App Router) | SSR, performans, Vercel deploy kolaylığı |
| UI styling         | TailwindCSS      | 3.x               | Hızlı geliştirme                         |
| Animasyon          | Framer Motion    | 11.x              | Yükleme animasyonları                    |
| Grafik             | Recharts         | 2.x               | React uyumlu, sade                       |
| Backend framework  | FastAPI          | 0.111.x           | Async, hızlı, otomatik OpenAPI           |
| Python versiyonu   | 3.11+            | —                 | asyncio performansı                      |
| HTTP client        | httpx            | —                 | Async scraping                           |
| AI API             | Gemini 1.5 Flash | —                 | Hız + maliyet dengesi                    |
| Veritabanı         | PostgreSQL       | 16                | Analiz cache için                        |
| Cache              | Redis            | 7.x               | URL bazlı cache                          |
| Scraping servisi   | ScraperAPI       | —                 | Hackathon; Firecrawl da kullanılabilir   |
| Deploy (FE)        | Vercel           | —                 | Zero config Next.js deploy               |
| Deploy (BE)        | Railway / Render | —                 | FastAPI için kolay deploy                |

---

## 9. AI & Analiz Motoru

### 9.1 Yorum Toplama & Ön İşleme

```python
class ReviewPreprocessor:
    def clean_text(self, text: str) -> str:
        # HTML tag temizleme
        # Emoji normalizasyonu (koru, metne çevirme)
        # Boşluk normalizasyonu
        # Türkçe karakter koruması

    def extract_metadata(self, review: dict) -> ReviewMeta:
        # Tarih parse etme
        # Yıldız puanı normalize etme (1-5 → 0-1)
        # Kullanıcı adı hashle (gizlilik)
```

### 9.2 Bot Tespit Algoritması

Bot tespiti kural tabanlı + Gemini destekli hibrit yaklaşımla çalışır.

#### Kural Tabanlı Sinyaller (Ağırlıklı)

| Sinyal                          | Ağırlık | Açıklama                                           |
| ------------------------------- | ------- | -------------------------------------------------- |
| **Tarih kümelenmesi**           | 0.25    | 24 saat içinde 10+ yorum aynı ürüne → şüpheli      |
| **Metin benzerliği**            | 0.25    | TF-IDF cosine similarity > 0.85 arası yorumlar     |
| **Yıldız-metin çelişkisi**      | 0.20    | 5 yıldız vermiş ama negatif kelimeler kullanmış    |
| **Çok kısa yorum**              | 0.10    | < 10 karakter ve 5 yıldız                          |
| **Genel ifade kalıpları**       | 0.10    | "Teşekkürler", "Süper geldi", "Güzel ürün" tekrarı |
| **Kullanıcı aktivite örüntüsü** | 0.10    | Aynı kullanıcı başka ürünleri de toplu yorumlamış  |

#### Gemini Destekli Analiz

50 yorum kümeleri halinde Gemini'a gönderilir. Prompt:

```
Aşağıdaki e-ticaret yorumlarını incele. Her yorum için:
1. İnsan mı, bot mu? (0-1 arası skor)
2. Eğer şüpheliyse neden?

Kriterlerin: doğallık, özgünlük, bağlamsal uygunluk, dil kalitesi.
Türkçe yorumlar için Türkçe doğallığını değerlendir.

Yorumlar: [JSON array]

Yanıtı sadece JSON olarak ver: [{"review_id": X, "bot_score": 0.X, "reason": "..."}]
```

#### Kombinasyon Formülü

```python
final_bot_score = (rule_score * 0.6) + (gemini_score * 0.4)
```

### 9.3 Duygu Analizi

#### Kategori Tespiti

Gemini ile her yorum kategorilere etiketlenir:

```
Sistem promptu:
"Türkçe e-ticaret yorumunu analiz et.
Hangi konuları kapsıyor?
Kategoriler: kargo, kalite, satıcı, fiyat, paketleme, beden/uyum, teknik
Her kategori için duygu: pozitif/negatif/nötr"
```

#### Agregasyon

Her kategori için:

- Pozitif yorum sayısı / Toplam yorum sayısı = Kategori skoru

### 9.4 Risk Skoru Hesaplama

```python
def calculate_risk_score(analysis: AnalysisData) -> int:
    """
    Risk skoru 0-100 arası (0 = güvenli, 100 = çok riskli)
    """

    # Bileşen skorları (her biri 0-100)
    bot_component = analysis.bot_percentage  # %38 bot → 38 puan

    quality_negative_rate = analysis.categories['kalite'].negative_ratio * 100

    recent_complaint_trend = calculate_trend_score(
        analysis.recent_complaints,  # Son 30 gün
        analysis.historical_complaints  # Tüm zamanlar
    )

    star_inflation = calculate_inflation(
        analysis.platform_rating,    # Platform gösterdiği
        analysis.weighted_real_rating  # Bot filtreli gerçek
    ) * 100

    return_complaints = analysis.categories.get('iade', CategoryData()).negative_ratio * 100

    # Ağırlıklı ortalama
    risk_score = (
        bot_component * 0.30 +
        quality_negative_rate * 0.25 +
        recent_complaint_trend * 0.20 +
        star_inflation * 0.15 +
        return_complaints * 0.10
    )

    return round(min(100, max(0, risk_score)))
```

#### Risk Kategorileri

| Skor   | Renk       | Etiket     | UI                                   |
| ------ | ---------- | ---------- | ------------------------------------ |
| 0-30   | 🟢 Yeşil   | Güvenilir  | "Güvenle alabilirsin"                |
| 31-60  | 🟡 Sarı    | Dikkatli   | "Dikkatli ol, şunlara bak:"          |
| 61-80  | 🟠 Turuncu | Riskli     | "Riskli, alternatifleri değerlendir" |
| 81-100 | 🔴 Kırmızı | Çok Riskli | "Satın almamayı öneriyoruz"          |

### 9.5 AI Özet Üretimi

```
Sistem promptu (Gemini):
"Sen bir tüketici hakları uzmanısın.
Aşağıdaki e-ticaret ürün analiz verilerini kullanarak
Türkçe, açık ve pratik bir özet yaz.

Veriler:
- Ürün: {product_name}
- Platform puanı: {platform_rating}
- Gerçek tahmini puan: {real_rating}
- Bot oranı: {bot_percentage}%
- Kategori analizi: {category_summary}
- En sık şikayetler: {top_complaints}
- En sık övgüler: {top_praises}
- Son 30 gün trendi: {trend}

Formatın:
1. Tek cümlelik genel değerlendirme
2. 'Kullanıcılar bundan şikayet ediyor:' (3-5 madde)
3. 'Kullanıcılar bunu seviyor:' (2-3 madde)
4. 'Dikkat et:' (1-2 kritik uyarı)

Abartma, tarafsız ol. Maksimum 150 kelime."
```

### 9.6 Zaman Bazlı Trend Analizi

```python
def analyze_complaint_trend(reviews: List[Review]) -> TrendData:
    # Son 30 gün vs önceki 30 gün karşılaştırması
    recent = [r for r in reviews if r.date >= 30_days_ago]
    previous = [r for r in reviews if 60_days_ago <= r.date < 30_days_ago]

    recent_negative_rate = calculate_negative_rate(recent)
    previous_negative_rate = calculate_negative_rate(previous)

    trend_change = recent_negative_rate - previous_negative_rate

    return TrendData(
        direction="increasing" if trend_change > 0.05 else "stable" if abs(trend_change) < 0.05 else "decreasing",
        change_percentage=trend_change * 100,
        alert=trend_change > 0.15  # %15+ artış varsa uyarı
    )
```

---

## 10. Veri Modeli

### 10.1 Review (Yorum)

```python
class Review(BaseModel):
    id: str
    text: str
    rating: int                    # 1-5
    date: datetime
    user_hash: str                 # SHA256 hash
    verified_purchase: bool
    helpful_count: int

    # Analiz sonuçları (işlendikten sonra)
    bot_score: float | None        # 0.0-1.0
    sentiment: str | None          # positive/negative/neutral
    categories: list[str] | None   # ["kargo", "kalite"]
```

### 10.2 AnalysisResult (Analiz Sonucu)

```python
class AnalysisResult(BaseModel):
    id: str                        # UUID
    url: str
    created_at: datetime
    cache_expires_at: datetime     # 6 saat cache

    # Ürün bilgisi
    product: ProductInfo

    # Yorum istatistikleri
    total_reviews_found: int
    total_reviews_analyzed: int

    # Bot analizi
    bot_percentage: float
    suspicious_review_count: int

    # Puan analizi
    platform_rating: float
    real_estimated_rating: float

    # Kategori bazlı analiz
    categories: dict[str, CategoryAnalysis]

    # Trend
    trend: TrendData

    # AI özeti
    ai_summary: str
    top_complaints: list[str]
    top_praises: list[str]
    sample_reviews: SampleReviews  # Pozitif + negatif örnekler

    # Risk
    risk_score: int                # 0-100
    risk_level: str                # safe/caution/risky/very_risky
    risk_explanation: str

    # Sürdürülebilirlik
    co2_saved_grams: float         # Tahmini tasarruf

class ProductInfo(BaseModel):
    name: str
    image_url: str
    price: str
    platform: str                  # trendyol/amazon/hepsiburada
    category: str

class CategoryAnalysis(BaseModel):
    name: str
    positive_count: int
    negative_count: int
    neutral_count: int
    positive_ratio: float
    sentiment_summary: str

class SampleReviews(BaseModel):
    most_reliable_positive: list[Review]   # Bot skoru düşük pozitif
    most_critical_negative: list[Review]   # Güvenilir negatif
```

### 10.3 Veritabanı Tabloları

```sql
-- Analiz cache tablosu
CREATE TABLE analysis_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_hash VARCHAR(64) UNIQUE NOT NULL,  -- SHA256(normalized_url)
    url TEXT NOT NULL,
    result JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    hit_count INTEGER DEFAULT 0
);

-- İndeks
CREATE INDEX idx_cache_url_hash ON analysis_cache(url_hash);
CREATE INDEX idx_cache_expires ON analysis_cache(expires_at);

-- Analiz istatistikleri (toplam etki ölçümü için)
CREATE TABLE platform_stats (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    total_analyses INTEGER DEFAULT 0,
    total_co2_saved_grams BIGINT DEFAULT 0,
    avg_risk_score FLOAT,
    avg_bot_percentage FLOAT
);
```

---

## 11. API Kontratları

### 11.1 POST /analyze

**İstek:**

```json
{
  "url": "https://www.trendyol.com/brand/product-name-p-12345678"
}
```

**Başarılı Yanıt (200):**

```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "cached": false,
  "product": {
    "name": "Örnek Ürün Adı",
    "image_url": "https://cdn.trendyol.com/...",
    "price": "₺299,99",
    "platform": "trendyol",
    "category": "elektronik"
  },
  "review_stats": {
    "total_found": 847,
    "total_analyzed": 200,
    "date_range": {
      "oldest": "2023-01-15",
      "newest": "2026-05-01"
    }
  },
  "bot_analysis": {
    "bot_percentage": 38.5,
    "suspicious_count": 77,
    "confidence": "high"
  },
  "rating_analysis": {
    "platform_rating": 4.6,
    "real_estimated_rating": 3.1,
    "inflation_detected": true
  },
  "categories": {
    "kalite": {
      "name": "Ürün Kalitesi",
      "positive_ratio": 0.35,
      "negative_ratio": 0.55,
      "neutral_ratio": 0.1,
      "summary": "Kullanıcıların yarısından fazlası kaliteden memnun değil"
    },
    "kargo": {
      "name": "Kargo & Teslimat",
      "positive_ratio": 0.72,
      "negative_ratio": 0.18,
      "neutral_ratio": 0.1,
      "summary": "Kargo genel olarak tatmin edici"
    }
  },
  "trend": {
    "direction": "increasing",
    "change_percentage": 23.5,
    "alert": true,
    "alert_message": "Son 30 günde şikayet oranı %24 arttı"
  },
  "ai_summary": {
    "overall": "Bu ürün kalite ve beden konusunda ciddi sorunlar yaşatıyor.",
    "complaints": [
      "Ürün fotoğraftaki gibi değil",
      "Beden tablosu yanıltıcı, küçük geliyor",
      "Batarya beklentinin çok altında"
    ],
    "praises": ["Kargo hızlı geldi", "Paketleme iyiydi"],
    "warnings": [
      "Son 1 ayda iade şikayetleri ciddi arttı",
      "Yorumların %38'i bot veya manipüle olabilir"
    ]
  },
  "risk_score": 67,
  "risk_level": "risky",
  "risk_explanation": "Yüksek bot oranı, artan kalite şikayetleri ve son dönem iade artışı bu ürünü riskli yapıyor.",
  "sample_reviews": {
    "most_reliable_negative": [
      {
        "text": "Ürün resimde göründüğünden çok farklı...",
        "rating": 2,
        "date": "2026-04-28",
        "bot_score": 0.05
      }
    ],
    "most_reliable_positive": [
      {
        "text": "Fiyatına göre idare eder ama...",
        "rating": 4,
        "date": "2026-04-15",
        "bot_score": 0.08
      }
    ]
  },
  "sustainability": {
    "co2_saved_grams": 120,
    "message": "Bu analiz ~120g CO₂ tasarrufu sağlayabilir"
  }
}
```

**Hata Yanıtları:**

```json
// 422 - Geçersiz URL
{
  "error": "invalid_url",
  "message": "Geçerli bir Trendyol ürün linki girin.",
  "supported_platforms": ["trendyol"]
}

// 503 - Scraping hatası
{
  "error": "scraping_failed",
  "message": "Ürün bilgilerine şu an ulaşılamıyor.",
  "retry_after": 30
}
```

### 11.2 GET /analyze/{analysis_id}

Daha önce yapılmış analizi getirir. Cache süresi: 6 saat.

### 11.3 GET /stats

Platform geneli istatistikler (landing page için).

```json
{
  "total_analyses": 1247,
  "total_co2_saved_kg": 149.64,
  "avg_bot_percentage": 31.2,
  "most_analyzed_categories": ["elektronik", "giyim", "kozmetik"]
}
```

---

## 12. UI/UX Gereksinimleri

### 12.1 Tasarım İlkeleri

- **Güven ve Netlik:** Bir güvenlik ürünü gibi hissettirmeli. Temiz, profesyonel, iddia ettiği şeyi açıkça göstermeli.
- **Anında Anlama:** Risk skoru sayfa yüklenir yüklenmez anlaşılmalı. Renk + sayı + etiket birlikte.
- **Sadelik:** Veri yoğun ama karmaşık değil. Her kart tek bir şeyi anlatır.
- **Mobil önce:** Responsive tasarım. Özellikle sonuç sayfası mobilde rahat okunmalı.

### 12.2 Renk Paleti

| Token          | Hex       | Kullanım                    |
| -------------- | --------- | --------------------------- |
| Güvenli        | `#16A34A` | Risk 0-30                   |
| Dikkatli       | `#EAB308` | Risk 31-60                  |
| Riskli         | `#F97316` | Risk 61-80                  |
| Çok Riskli     | `#DC2626` | Risk 81-100                 |
| Birincil       | `#1E40AF` | CTA, butonlar               |
| Arka Plan      | `#F8FAFC` | Sayfa zemini                |
| Kart           | `#FFFFFF` | Kart arka planı             |
| Metin          | `#0F172A` | Ana metin                   |
| Yardımcı metin | `#64748B` | İkincil metin               |
| Yeşil (karbon) | `#059669` | Sürdürülebilirlik rozetleri |

### 12.3 Landing Page Bileşenleri

```
┌─────────────────────────────────────────────────────┐
│  🔍 GerçekSepet                          [GitHub] │
├─────────────────────────────────────────────────────┤
│                                                     │
│         Satın Almadan Önce                          │
│              Gerçeği Gör                            │
│                                                     │
│   Yorumları biz okuyoruz. Botları biz buluyoruz.   │
│         Senin işin sadece karar vermek.             │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ 🔗 Trendyol ürün linkini buraya yapıştır...  │   │
│  └─────────────────────────────────────────────┘   │
│              [ Analiz Et → ]                        │
│                                                     │
│   ✓ Ücretsiz  ✓ Kayıt gerekmez  ✓ 30 saniyede    │
├─────────────────────────────────────────────────────┤
│  Bugün: 1.247 analiz | 149 kg CO₂ tasarrufu 🌱     │
├─────────────────────────────────────────────────────┤
│  Nasıl Çalışır?                                     │
│  1️⃣ Link yapıştır  2️⃣ AI analiz eder  3️⃣ Gerçeği gör │
└─────────────────────────────────────────────────────┘
```

### 12.4 Analiz Sonuç Sayfası Bileşenleri

#### Bileşen Hiyerarşisi ve Öncelik Sırası

1. **ProductCard** — Ürün adı, görseli, fiyatı, platform
2. **RiskScoreHero** — Dev risk skoru, renk, etiket (fold üstü)
3. **BotAnalysisSection** — Bot oranı, görselleştirme, açıklama
4. **RatingComparison** — Platform puanı vs gerçek tahmini puan
5. **CategoryBreakdown** — Kategori bazlı duygu çubuk grafikleri
6. **TrendSection** — 30/60 günlük şikayet trendi çizgi grafiği
7. **AISummary** — Şikayetler, övgüler, uyarılar
8. **SampleReviews** — Seçilmiş yorumlar (güvenilirlik skoru ile)
9. **CarbonBadge** — CO₂ tasarruf tahmini
10. **ShareCTA** — Paylaşım butonları

### 12.5 Yükleme Animasyonu

```
GerçekSepet Çalışıyor...

[████████░░░░░░░░░░░░] 45%

✅ Ürün bilgileri alındı
✅ 847 yorum bulundu, 200 analiz edildi
🔄 Bot analizi yapılıyor...
⏳ AI yorumları değerlendiriyor...
⏳ Risk skoru hesaplanıyor...

Bu işlem 15-30 saniye sürebilir.
```

### 12.6 Erişilebilirlik (A11y) Gereksinimleri

- Tüm renkler WCAG AA kontrast oranı (4.5:1) sağlamalı
- Risk göstergesi renk + ikon + metin kombinasyonu (renk körlüğü)
- Tab navigasyonu destekli
- Screen reader için ARIA label'lar
- Türkçe lang="tr" HTML attribute'u

---

## 13. Scraping Stratejisi

### 13.1 Hackathon Dönemi (v0.1)

**ScraperAPI** kullanılacak. Free plan: 1.000 istek/ay.

```python
import httpx

class TrendyolScraper:
    BASE_URL = "http://api.scraperapi.com"

    async def scrape_product_page(self, product_url: str) -> dict:
        params = {
            "api_key": settings.SCRAPER_API_KEY,
            "url": product_url,
            "render": "true",  # JavaScript render
            "country_code": "tr"
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(self.BASE_URL, params=params)
            return self._parse_html(response.text)

    async def scrape_reviews_page(self, product_id: str, page: int) -> list[dict]:
        # Trendyol review API endpoint (reverse engineered)
        review_url = f"https://public-mdc.trendyol.com/discovery-web-websfxproductrating-santral/api/product-reviews?productId={product_id}&page={page}"

        params = {
            "api_key": settings.SCRAPER_API_KEY,
            "url": review_url
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(self.BASE_URL, params=params)
            return response.json()
```

**Not:** Trendyol'un iç API endpoint'leri (public-mdc domain) public-facing ve authentication gerektirmiyor. Bu endpoint'ler browser'da da erişilebilir durumda.

### 13.2 Üretim (v1.0)

**Seçenek A — Ölçekli Scraping Servisi:**

- Bright Data / Oxylabs — ticari scraping, kendi TOS uyumluluklarını yönetiyorlar
- Maliyet: ~$50-500/ay (kullanıma göre)

**Seçenek B — Chrome Extension ile Client-Side (Önerilen):**

- Extension sayfanın DOM'unu okur → server'a yorum verilerini gönderir
- Server tarafında scraping yok → TOS ihlali yok
- Bu Fakespot'ın çalışma modelidir

**Seçenek C — Platform Ortaklıkları:**

- Trendyol Partner API müzakereleri (uzun vadeli)
- Resmi veri erişimi

**Hackathon için tercih:** Seçenek A (ScraperAPI) hızlı çalışır. Chrome Extension yetişirse Seçenek B ekle.

### 13.3 Trendyol Sayfa Analizi

Trendyol'da yorumlar için kullanılabilecek endpoint yapısı:

```
Ürün ID'si URL'den extract edilir:
https://www.trendyol.com/marka/urun-adi-p-{PRODUCT_ID}

Yorum endpoint'i (public, auth yok):
GET public-mdc.trendyol.com/discovery-web-websfxproductrating-santral/api/product-reviews
  ?productId={PRODUCT_ID}
  &page={PAGE_NUMBER}
  &pageSize=50
  &star=0  (0 = tüm yıldızlar)
```

Sayfalama: Her sayfada max 50 yorum. İlk 4 sayfa (200 yorum) yeterli.

---

## 14. Chrome Extension

### 14.1 Mimari

```
Chrome Extension (Manifest V3)
├── manifest.json
├── background/
│   └── service_worker.js    # Background service worker
├── content/
│   └── content_script.js    # Trendyol sayfasında DOM okuma
├── popup/
│   ├── popup.html
│   ├── popup.css
│   └── popup.js             # Mini analiz sonucu
└── icons/
```

### 14.2 manifest.json

```json
{
  "manifest_version": 3,
  "name": "GerçekSepet",
  "version": "0.1.0",
  "description": "Satın almadan önce gerçeği gör.",
  "permissions": ["activeTab", "storage"],
  "host_permissions": [
    "https://www.trendyol.com/*",
    "https://www.amazon.com.tr/*",
    "https://www.hepsiburada.com/*"
  ],
  "action": {
    "default_popup": "popup/popup.html",
    "default_icon": "icons/icon48.png"
  },
  "content_scripts": [
    {
      "matches": ["https://www.trendyol.com/*"],
      "js": ["content/content_script.js"],
      "run_at": "document_idle"
    }
  ]
}
```

### 14.3 Content Script — DOM Okuma

```javascript
// content_script.js
// Trendyol ürün sayfasında DOM'dan yorumları toplar
// Server scraping YOK — TOS uyumlu

function isProductPage() {
  return window.location.pathname.includes("-p-");
}

function extractProductId() {
  const match = window.location.pathname.match(/-p-(\d+)/);
  return match ? match[1] : null;
}

function extractReviews() {
  const reviewElements = document.querySelectorAll(".comment-container");
  return Array.from(reviewElements)
    .map((el) => ({
      text: el.querySelector(".comment-text")?.textContent?.trim(),
      rating: el.querySelectorAll(".star-fill").length,
      date: el.querySelector(".comment-date")?.textContent?.trim(),
    }))
    .filter((r) => r.text);
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getReviews") {
    sendResponse({
      productId: extractProductId(),
      reviews: extractReviews(),
      isProductPage: isProductPage(),
    });
  }
});
```

### 14.4 Popup Akışı

```javascript
// popup.js
document.addEventListener("DOMContentLoaded", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  // İçerik script'ten verileri al
  const data = await chrome.tabs.sendMessage(tab.id, { action: "getReviews" });

  if (!data.isProductPage) {
    showMessage("Trendyol ürün sayfasında olun.");
    return;
  }

  showLoading();

  // Backend'e gönder
  const response = await fetch(
    "https://api.gerçeksepet.com/analyze-extension",
    {
      method: "POST",
      body: JSON.stringify({
        product_id: data.productId,
        reviews: data.reviews,
        source_url: tab.url,
      }),
    },
  );

  const result = await response.json();
  showMiniResult(result);
});
```

---

## 15. Güvenlik & Gizlilik

### 15.1 Kullanıcı Gizliliği

- Kullanıcı herhangi bir kişisel bilgi vermek zorunda değil (v0.1'de kayıt yok)
- URL'ler hash'lenerek saklanır (cache için)
- Yorum kullanıcı adları SHA-256 ile hash'lenir
- Hiçbir IP adresi loglanmaz

### 15.2 API Güvenliği

```python
# Rate limiting — kötüye kullanım engeli
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze")
@limiter.limit("10/minute")  # IP başına dakikada 10 istek
async def analyze(request: Request, body: AnalyzeRequest):
    ...
```

- CORS: Sadece gerçeksepet.com domainine izin
- Input validasyonu: Pydantic ile URL formatı kontrolü
- API key'ler environment variable'da (hardcode yok)

### 15.3 Scraping Riski Yönetimi

- Scraping istekleri ScraperAPI üzerinden → IP maskeleme
- User-agent rotation
- İstek arası bekleme süresi (rate limiting'e uymak için)
- Robots.txt'e saygı (demo dışı)

---

## 16. Performans Gereksinimleri

### 16.1 Hız Hedefleri

| Metrik                  | Hedef   | Kritik Sınır |
| ----------------------- | ------- | ------------ |
| İlk yorum scrape        | < 10sn  | < 20sn       |
| Toplam analiz süresi    | < 30sn  | < 60sn       |
| Sayfa yükleme (sonuç)   | < 1sn   | < 2sn        |
| Cache'den sonuç getirme | < 200ms | < 500ms      |

### 16.2 Cache Stratejisi

```python
CACHE_TTL_HOURS = 6  # Aynı URL 6 saat içinde tekrar analiz edilirse cache'den gelir

async def get_or_create_analysis(url: str) -> AnalysisResult:
    url_hash = hashlib.sha256(normalize_url(url).encode()).hexdigest()

    # Cache kontrol
    cached = await db.get_cached_analysis(url_hash)
    if cached and cached.expires_at > datetime.now():
        await db.increment_hit_count(url_hash)
        return cached.result

    # Yeni analiz
    result = await run_full_analysis(url)
    await db.save_analysis(url_hash, url, result, ttl_hours=6)
    return result
```

### 16.3 Asenkron İşlem

```python
# Scraping ve AI işlemleri paralel çalışır

async def run_full_analysis(url: str) -> AnalysisResult:
    # 1. Scraping (sıralı: ürün bilgisi → yorumlar)
    product_info = await scraper.get_product_info(url)
    reviews = await scraper.get_all_reviews(product_info.id, max_pages=4)

    # 2. Bot tespiti + Duygu analizi (paralel)
    bot_task = asyncio.create_task(bot_detector.analyze(reviews))
    sentiment_task = asyncio.create_task(sentiment_analyzer.analyze(reviews))

    bot_results, sentiment_results = await asyncio.gather(bot_task, sentiment_task)

    # 3. Risk hesaplama + AI özet (paralel)
    risk_task = asyncio.create_task(risk_calculator.calculate(bot_results, sentiment_results))
    summary_task = asyncio.create_task(gemini_service.generate_summary(product_info, bot_results, sentiment_results))

    risk_score, ai_summary = await asyncio.gather(risk_task, summary_task)

    return AnalysisResult(...)
```

---

## 17. Ölçme & Başarı Kriterleri

### 17.1 Hackathon Başarı Kriterleri

| Kriter                             | Hedef |
| ---------------------------------- | ----- |
| Demo çalışıyor (canlı)             | Evet  |
| Gerçek Trendyol URL'iyle analiz    | Evet  |
| 30 saniye içinde sonuç             | Evet  |
| Risk skoru görünür ve anlaşılır    | Evet  |
| Bot oranı görünür                  | Evet  |
| AI özeti anlamlı                   | Evet  |
| CO₂ bağlantısı sunumda açıklanıyor | Evet  |
| Jüri sorusuna teknik cevap hazır   | Evet  |

### 17.2 Ürün Kuzey Yıldızı Metriği (v1.0)

**"Analiz Başına Önlenen Yanlış Alım"** (proxy: risk skoru 61+ olan ürünlerde kullanıcının alışverişten vazgeçmesi)

### 17.3 İzleme Metrikleri

| Metrik                   | Açıklama                           |
| ------------------------ | ---------------------------------- |
| Daily Active Analyses    | Günlük yapılan analiz sayısı       |
| URL Cache Hit Rate       | Cache verimliliği                  |
| Avg Analysis Time        | Ortalama analiz süresi             |
| Bot Detection Confidence | Yüksek güvenilirlik oranı          |
| Share Rate               | Analiz → paylaşım dönüşümü         |
| Return Rate              | Kullanıcıların tekrar dönüşü       |
| CO₂ Impact (Toplam)      | Platform geneli karbondan tasarruf |

---

## 18. Roadmap

### v0.1 — Hackathon (48 Saat)

**Hedef:** Çalışan demo, jüriye sunulabilir prototip

| Gün                 | Görev                                          | Sorumlu            |
| ------------------- | ---------------------------------------------- | ------------------ |
| Gün 1 Sabah         | FastAPI skeleton, Trendyol scraper             | Backend            |
| Gün 1 Öğleden sonra | Bot tespit algoritması (kural tabanlı)         | Backend            |
| Gün 1 Akşam         | Gemini entegrasyonu, risk skoru                | AI + Backend       |
| Gün 1 Gece          | Next.js landing + analiz sayfası iskelet       | Frontend           |
| Gün 2 Sabah         | UI bileşenleri (Risk gauge, kategori kartları) | Frontend           |
| Gün 2 Öğleden sonra | API entegrasyonu, loading states               | Frontend + Backend |
| Gün 2 Akşam         | Demo ürünler test, bug fix, sunum hazırlığı    | Tüm ekip           |

### v0.2 — Post-Hackathon (1-2 Hafta)

- Kullanıcı hesabı (Auth.js)
- Amazon TR desteği
- Hepsiburada desteği
- Analiz geçmişi
- Performans iyileştirmeleri

### v1.0 — MVP (1-2 Ay)

- Chrome Extension yayınlama
- Ürün karşılaştırma
- Fiyat + güvenilirlik takibi
- E-posta bildirimleri
- Kullanıcı geri bildirimi sistemi ("Analiz doğru muydu?")

### v2.0 — Büyüme (3-6 Ay)

- React Native mobil uygulama
- N11, GittiGidiyor desteği
- B2B API (markalar için şikayet analizi)
- Çoklu dil desteği
- Makine öğrenmesi tabanlı bot tespiti (eğitilmiş model)

---

## 19. Riskler & Azaltma Stratejileri

| Risk                               | Olasılık | Etki       | Azaltma                                                            |
| ---------------------------------- | -------- | ---------- | ------------------------------------------------------------------ |
| Scraping bloklama (demo sırasında) | Orta     | Çok Yüksek | ScraperAPI kullan, mock data backup hazır tut                      |
| Gemini API rate limit              | Düşük    | Yüksek     | İstek batching, cache, retry logic                                 |
| Trendyol sayfa yapısı değişimi     | Orta     | Yüksek     | Ayrıştırıcı modüler yaz, kolayca güncellenebilir                   |
| Yanlış bot tespiti                 | Orta     | Orta       | "Şüpheli olabilir" dili kullan, kesin iddia etme                   |
| Hukuki (TOS ihlali)                | Yüksek   | Orta       | Hackathon için göz yumulabilir; üretim için extension modeline geç |
| Gemini hallüsinasyonu              | Düşük    | Orta       | Özeti veriye dayalı prompt'la oluştur, kontrollü format            |
| Yorum sayısı az ürün               | Orta     | Düşük      | Minimum yorum sayısı kontrolü (10+), uyarı mesajı                  |

### 19.1 Demo Güvenceleri

Hackathon sunumu için **mock data backup** hazır olacak. Eğer scraping canlı demo'da başarısız olursa, önceden çekilmiş ve analiz edilmiş gerçek bir ürünün sonuçları "önbelleğe alınmış analiz" etiketi ile gösterilecek. Bu tamamen gerçekçi ve kabul edilebilir bir fallback'tir.

```python
# Fallback data
DEMO_CACHED_ANALYSES = {
    "demo_product_1": {
        "product": {"name": "...", "image_url": "..."},
        "risk_score": 67,
        # ... tam analiz verisi
    }
}
```

---

## 20. Hackathon Demo Planı

### 20.1 Demo Senaryosu (5 Dakika)

**[0:00-0:30] Problem**

> "Trendyol'da bir ürün bakıyorsunuz. 4.8 yıldız, 1.200 yorum. Satın aldınız. Geldi. Hiç benzemiyor. Paranızı, zamanınızı kaybettiniz. Bu Türkiye'de her gün milyonlarca kez yaşanıyor."

**[0:30-1:00] Çözüm Tanıtımı**

> "GerçekSepet. Satın almadan önce gerçeği görün."

**[1:00-3:30] Canlı Demo**

1. Trendyol'dan riskli bir ürün URL'si kopyala (önceden seçilmiş)
2. GerçekSepet'e yapıştır → Analiz Et
3. 15-30 sn yükleme (animasyonlu adımlar)
4. Sonucu göster: Risk 67/100, %38 bot, azalan kalite yorumları
5. AI özetini oku
6. "Platformun gösterdiği 4.6 yıldız, gerçek kullanıcı hissiyatı 3.1 yıldız"

**[3:30-4:00] Sürdürülebilirlik Bağlantısı**

> "Her önlenen yanlış alım = önlenen iade = önlenen kargo emisyonu. Bu analiz ~120g CO₂ tasarrufu sağladı. Platform genelinde bugün 149 kg CO₂."

**[4:00-4:30] Vizyon**

> "Trendyol'dan başladık. Amazon, Hepsiburada geliyor. Chrome extension yayında olacak. Hedef: e-ticarette bilgi asimetrisini ortadan kaldırmak."

**[4:30-5:00] Kapanış**

> "GerçekSepet — Yorumları biz okuyoruz, siz sadece karar verin."

### 20.2 Demo için Hazırlanacak Ürünler

Jüri önünde demo yapılacak 3 ürün önceden seçilip test edilmeli:

1. **Yüksek Riskli Ürün** (Risk 70+): Bot oranı yüksek, kalite şikayeti fazla, wow effect
2. **Orta Riskli Ürün** (Risk 40-60): Karma sonuç, "dikkatli ol" mesajı
3. **Güvenilir Ürün** (Risk <30): GerçekSepet'in doğrulama yapabildiğini de göster

### 20.3 Olası Jüri Soruları & Cevaplar

**"Bot tespiti nasıl çalışıyor?"**

> Kural tabanlı sinyaller (tarih kümelenmesi, metin benzerliği, yıldız-metin çelişkisi) + Gemini AI'ın dil analizi. İkisini ağırlıklı birleştiriyoruz.

**"Scraping yasadışı değil mi?"**

> Prototip aşamasında ScraperAPI kullanıyoruz. Üretimde Chrome Extension modeline geçiyoruz — kullanıcının kendi tarayıcısı sayfa DOM'unu okuyor, server tarafında scraping yok. Fakespot'ın Mozilla tarafından satın alındığı model bu.

**"Trendyol bunu bloklar mı?"**

> Bu tam olarak extension modeline geçme sebebimiz. Uzun vadede platform API ortaklıkları da hedefliyoruz.

**"Rakibiniz var mı?"**

> Fakespot (Amazon, İngilizce), ReviewMeta (Amazon, İngilizce). Türkiye pazarı ve Trendyol için özel çözüm yok. Burası bizim.

**"Nasıl para kazanacaksınız?"**

> Freemium: aylık 20 analize kadar ücretsiz, sonrası abonelik. B2B: markalara şikayet analizi API'si.

---

## EKLER

### Ek A: Teknik Bağımlılıklar

```
# Backend (requirements.txt)
fastapi==0.111.0
uvicorn[standard]==0.29.0
httpx==0.27.0
pydantic==2.7.0
sqlalchemy==2.0.29
asyncpg==0.29.0
redis==5.0.4
google-generativeai==0.5.4
beautifulsoup4==4.12.3
scikit-learn==1.4.2    # TF-IDF cosine similarity
slowapi==0.1.9          # Rate limiting
python-dotenv==1.0.1

# Frontend (package.json)
next: ^14.2.0
react: ^18.3.0
tailwindcss: ^3.4.0
framer-motion: ^11.0.0
recharts: ^2.12.0
@radix-ui/react-*: latest  # UI primitives
```

### Ek B: Ortam Değişkenleri

```env
# .env
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
REDIS_URL=redis://localhost:6379
SCRAPER_API_KEY=your_scraperapi_key
GEMINI_API_KEY=your_gemini_api_key
CORS_ORIGINS=http://localhost:3000,https://gerçeksepet.com
CACHE_TTL_HOURS=6
MAX_REVIEWS_PER_ANALYSIS=200
MIN_REVIEWS_REQUIRED=10
```

### Ek C: Desteklenen Platform URL Formatları

```python
PLATFORM_PATTERNS = {
    "trendyol": re.compile(r"https?://(?:www\.)?trendyol\.com/.+-p-(\d+)"),
    "amazon": re.compile(r"https?://(?:www\.)?amazon\.com\.tr/.+/dp/([A-Z0-9]{10})"),
    "hepsiburada": re.compile(r"https?://(?:www\.)?hepsiburada\.com/.+-pm-(.+)")
}
```

---

_GerçekSepet PRD v1.0 — Bu belge yaşayan bir döküman olup geliştirme sürecinde güncellenecektir._
