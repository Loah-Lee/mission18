from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Query, status

from .. import crud, schemas
from ..database import get_db
from ..services.sentiment import analyze_sentiment

router = APIRouter(tags=["reviews"])


@router.post("/reviews", response_model=schemas.ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(review_in: schemas.ReviewCreate, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, review_in.movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    sentiment_result = analyze_sentiment(review_in.content)
    return crud.create_review(
        db,
        review_in,
        sentiment_label=sentiment_result["label"],
        sentiment_score=sentiment_result["score"],
    )


@router.get("/reviews", response_model=list[schemas.ReviewRead])
def list_reviews(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return crud.get_reviews(db, limit=limit)


@router.get("/movies/{movie_id}/reviews", response_model=list[schemas.ReviewRead])
def list_movie_reviews(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return crud.get_reviews_by_movie(db, movie_id)


@router.delete("/reviews/{review_id}", response_model=schemas.DeleteResponse)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    review = crud.get_review(db, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    crud.delete_review(db, review)
    return {"detail": f"Review {review_id} deleted successfully"}
