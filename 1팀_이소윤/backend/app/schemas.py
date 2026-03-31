from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class MovieBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    release_date: date
    director: str = Field(..., min_length=1, max_length=255)
    genre: str = Field(..., min_length=1, max_length=255)
    poster_url: str = Field(..., min_length=1, max_length=1000)


class MovieCreate(MovieBase):
    pass


class MovieUpdate(MovieBase):
    pass


class MovieRead(MovieBase):
    id: int
    created_at: datetime
    average_rating: float | None = None

    model_config = ConfigDict(from_attributes=True)


class ReviewBase(BaseModel):
    author: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)


class ReviewCreate(ReviewBase):
    movie_id: int


class ReviewRead(ReviewBase):
    id: int
    movie_id: int
    sentiment_label: str
    sentiment_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RatingResponse(BaseModel):
    movie_id: int
    review_count: int
    average_rating: float | None = None


class DeleteResponse(BaseModel):
    detail: str
