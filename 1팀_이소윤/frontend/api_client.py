import os

import requests


def _resolve_backend_base_url() -> str:
    env_value = os.getenv("BACKEND_BASE_URL")
    if env_value:
        return env_value.rstrip("/")

    try:
        import streamlit as st

        secret_value = st.secrets.get("BACKEND_BASE_URL")
        if secret_value:
            return str(secret_value).rstrip("/")
    except Exception:
        pass

    return "http://localhost:8000"


BACKEND_BASE_URL = _resolve_backend_base_url()
TIMEOUT_SECONDS = 10


def _request(method: str, path: str, **kwargs):
    response = requests.request(
        method=method,
        url=f"{BACKEND_BASE_URL}{path}",
        timeout=TIMEOUT_SECONDS,
        **kwargs,
    )
    response.raise_for_status()
    return response.json()


def get_health():
    return _request("GET", "/health")


def get_movies():
    return _request("GET", "/movies")


def create_movie(payload: dict):
    return _request("POST", "/movies", json=payload)


def update_movie(movie_id: int, payload: dict):
    return _request("PUT", f"/movies/{movie_id}", json=payload)


def delete_movie(movie_id: int):
    return _request("DELETE", f"/movies/{movie_id}")


def get_recent_reviews(limit: int = 10):
    return _request("GET", f"/reviews?limit={limit}")


def get_movie_reviews(movie_id: int):
    return _request("GET", f"/movies/{movie_id}/reviews")


def create_review(payload: dict):
    return _request("POST", "/reviews", json=payload)


def delete_review(review_id: int):
    return _request("DELETE", f"/reviews/{review_id}")


def get_movie_rating(movie_id: int):
    return _request("GET", f"/movies/{movie_id}/rating")
