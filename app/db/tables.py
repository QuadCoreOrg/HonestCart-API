from datetime import datetime

from sqlalchemy import Date, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AnalysisCache(Base):
    __tablename__ = "analysis_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    hit_count: Mapped[int] = mapped_column(Integer, default=0)


class PlatformStats(Base):
    __tablename__ = "platform_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
    total_analyses: Mapped[int] = mapped_column(Integer, default=0)
    total_co2_saved_grams: Mapped[int] = mapped_column(Integer, default=0)
    avg_risk_score: Mapped[float] = mapped_column(nullable=True)
    avg_bot_percentage: Mapped[float] = mapped_column(nullable=True)


from datetime import date