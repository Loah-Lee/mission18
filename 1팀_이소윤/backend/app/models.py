from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    release_date: Mapped[date] = mapped_column(Date, nullable=False)
    director: Mapped[str] = mapped_column(String(255), nullable=False)
    genre: Mapped[str] = mapped_column(String(255), nullable=False)
    poster_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    reviews: Mapped[list["Review"]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan",
    )

    @property
    def average_rating(self) -> Optional[float]:
        if not self.reviews:
            return None
        average = sum(review.sentiment_score for review in self.reviews) / len(self.reviews)
        return round(average, 2)


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment_label: Mapped[str] = mapped_column(String(20), nullable=False)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    movie: Mapped["Movie"] = relationship(back_populates="reviews")
