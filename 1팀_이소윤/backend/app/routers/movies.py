from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/movies", tags=["movies"])


@router.post("", response_model=schemas.MovieRead, status_code=status.HTTP_201_CREATED)
def create_movie(movie_in: schemas.MovieCreate, db: Session = Depends(get_db)):
    return crud.create_movie(db, movie_in)


@router.get("", response_model=list[schemas.MovieRead])
def list_movies(db: Session = Depends(get_db)):
    return crud.get_movies(db)


@router.get("/{movie_id}", response_model=schemas.MovieRead)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie


@router.put("/{movie_id}", response_model=schemas.MovieRead)
def update_movie(movie_id: int, movie_in: schemas.MovieUpdate, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return crud.update_movie(db, movie, movie_in)


@router.get("/{movie_id}/rating", response_model=schemas.RatingResponse)
def get_movie_rating(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return crud.get_movie_rating(db, movie_id)


@router.delete("/{movie_id}", response_model=schemas.DeleteResponse)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    crud.delete_movie(db, movie)
    return {"detail": f"Movie {movie_id} deleted successfully"}
