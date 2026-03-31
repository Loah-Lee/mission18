from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from . import models, schemas


def create_movie(db: Session, movie_in: schemas.MovieCreate) -> models.Movie:
    movie = models.Movie(**movie_in.model_dump())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


def get_movies(db: Session) -> list[models.Movie]:
    statement = (
        select(models.Movie)
        .options(selectinload(models.Movie.reviews))
        .order_by(models.Movie.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_movie(db: Session, movie_id: int) -> models.Movie | None:
    statement = (
        select(models.Movie)
        .options(selectinload(models.Movie.reviews))
        .where(models.Movie.id == movie_id)
    )
    return db.scalars(statement).first()


def update_movie(
    db: Session,
    movie: models.Movie,
    movie_in: schemas.MovieUpdate,
) -> models.Movie:
    for field, value in movie_in.model_dump().items():
        setattr(movie, field, value)
    db.commit()
    db.refresh(movie)
    return movie


def delete_movie(db: Session, movie: models.Movie) -> None:
    db.delete(movie)
    db.commit()


def create_review(
    db: Session,
    review_in: schemas.ReviewCreate,
    sentiment_label: str,
    sentiment_score: float,
) -> models.Review:
    review = models.Review(
        **review_in.model_dump(),
        sentiment_label=sentiment_label,
        sentiment_score=sentiment_score,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_reviews(db: Session, limit: int = 10) -> list[models.Review]:
    statement = select(models.Review).order_by(models.Review.created_at.desc()).limit(limit)
    return list(db.scalars(statement).all())


def get_reviews_by_movie(db: Session, movie_id: int) -> list[models.Review]:
    statement = (
        select(models.Review)
        .where(models.Review.movie_id == movie_id)
        .order_by(models.Review.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_review(db: Session, review_id: int) -> models.Review | None:
    statement = select(models.Review).where(models.Review.id == review_id)
    return db.scalars(statement).first()


def delete_review(db: Session, review: models.Review) -> None:
    db.delete(review)
    db.commit()


def get_movie_rating(db: Session, movie_id: int) -> dict:
    statement = select(
        func.count(models.Review.id),
        func.avg(models.Review.sentiment_score),
    ).where(models.Review.movie_id == movie_id)
    review_count, average_rating = db.execute(statement).one()
    return {
        "movie_id": movie_id,
        "review_count": review_count,
        "average_rating": round(float(average_rating), 2) if average_rating is not None else None,
    }
