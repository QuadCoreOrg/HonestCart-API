from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: DB ve Redis bağlantıları hazır
    yield
    # Shutdown: temizlik


app = FastAPI(
    title="HonestCart API",
    description="E-ticaret ürün analiz API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Router'ları import et
from app.routers import analysis
app.include_router(analysis.router)