import pandas as pd
import streamlit as st
from datetime import date

from api_client import create_movie, delete_movie, get_movie_reviews, get_movies, update_movie

MIN_KOREAN_RELEASE_DATE = date(1900, 1, 1)
MAX_KOREAN_RELEASE_DATE = date.today()

st.title("영화")
st.caption("백엔드에 저장된 영화 정보를 확인하고 새 영화를 등록합니다.")

with st.form("create_movie_form", clear_on_submit=True):
    st.subheader("영화 추가")
    title = st.text_input("제목")
    release_date = st.date_input(
        "한국 개봉일",
        min_value=MIN_KOREAN_RELEASE_DATE,
        max_value=MAX_KOREAN_RELEASE_DATE,
    )
    director = st.text_input("감독")
    genre = st.text_input("장르")
    poster_url = st.text_input("포스터 URL")
    submitted = st.form_submit_button("영화 저장")

    if submitted:
        if not all([title, director, genre, poster_url]):
            st.warning("모든 항목을 입력한 뒤 저장하세요.")
        else:
            payload = {
                "title": title,
                "release_date": release_date.isoformat(),
                "director": director,
                "genre": genre,
                "poster_url": poster_url,
            }
            try:
                created = create_movie(payload)
                st.success(f"영화가 저장되었습니다: {created['title']}")
            except Exception as exc:
                st.error(f"영화 저장에 실패했습니다: {exc}")

st.divider()
st.subheader("영화 목록")

try:
    movies = get_movies()
except Exception as exc:
    st.error(f"영화 목록을 불러오지 못했습니다: {exc}")
    movies = []

movie_reviews_map = {}
for movie in movies:
    try:
        movie_reviews_map[movie["id"]] = get_movie_reviews(movie["id"])
    except Exception:
        movie_reviews_map[movie["id"]] = []

if movies:
    chart_rows = []
    for movie in movies:
        average_rating = movie["average_rating"] or 0
        review_count = len(movie_reviews_map.get(movie["id"], []))
        chart_rows.append(
            {
                "영화": movie["title"],
                "평균 평점": average_rating,
                "리뷰 수": review_count,
            }
        )

    ratings_df = pd.DataFrame(chart_rows).set_index("영화")
    st.subheader("영화별 평균 평점 비교")
    st.bar_chart(ratings_df["평균 평점"])
    st.caption("평균 평점은 등록된 리뷰의 감성 분석 점수 평균입니다.")

if not movies:
    st.info("아직 등록된 영화가 없습니다.")
else:
    for movie in movies:
        reviews = movie_reviews_map.get(movie["id"], [])
        review_count = len(reviews)
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(movie["poster_url"], use_container_width=True)
        with col2:
            st.markdown(f"### {movie['title']}")
            st.write(f"한국 개봉일: {movie['release_date']}")
            st.write(f"감독: {movie['director']}")
            st.write(f"장르: {movie['genre']}")
            if movie["average_rating"] is None:
                st.write("평균 평점: 아직 리뷰가 없습니다.")
                st.progress(0.0, text="평균 평점 시각화")
            else:
                st.write(f"평균 평점: {movie['average_rating']}")
                st.progress(
                    min(max(float(movie["average_rating"]) / 5.0, 0.0), 1.0),
                    text=f"5점 만점 기준 {movie['average_rating']}",
                )
            st.write(f"리뷰 수: {review_count}")

            if review_count:
                positive_count = sum(review["sentiment_label"] == "positive" for review in reviews)
                neutral_count = sum(review["sentiment_label"] == "neutral" for review in reviews)
                negative_count = sum(review["sentiment_label"] == "negative" for review in reviews)
                distribution_df = pd.DataFrame(
                    {
                        "개수": [positive_count, neutral_count, negative_count],
                    },
                    index=["긍정", "중립", "부정"],
                )
                st.bar_chart(distribution_df)

            with st.expander("영화 정보 수정"):
                with st.form(f"edit_movie_form_{movie['id']}"):
                    edit_title = st.text_input("제목", value=movie["title"])
                    edit_release_date = st.date_input(
                        "한국 개봉일",
                        value=date.fromisoformat(movie["release_date"]),
                        min_value=MIN_KOREAN_RELEASE_DATE,
                        max_value=MAX_KOREAN_RELEASE_DATE,
                        key=f"release_date_{movie['id']}",
                    )
                    edit_director = st.text_input("감독", value=movie["director"])
                    edit_genre = st.text_input("장르", value=movie["genre"])
                    edit_poster_url = st.text_input("포스터 URL", value=movie["poster_url"])
                    update_submitted = st.form_submit_button("수정 저장")

                    if update_submitted:
                        if not all([edit_title, edit_director, edit_genre, edit_poster_url]):
                            st.warning("모든 항목을 입력한 뒤 저장하세요.")
                        else:
                            payload = {
                                "title": edit_title,
                                "release_date": edit_release_date.isoformat(),
                                "director": edit_director,
                                "genre": edit_genre,
                                "poster_url": edit_poster_url,
                            }
                            try:
                                updated = update_movie(movie["id"], payload)
                                st.success(f"영화 정보가 수정되었습니다: {updated['title']}")
                                st.rerun()
                            except Exception as exc:
                                st.error(f"영화 수정에 실패했습니다: {exc}")

            if st.button("영화 삭제", key=f"delete_movie_{movie['id']}"):
                try:
                    delete_movie(movie["id"])
                    st.success(f"{movie['title']} 영화를 삭제했습니다.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"영화 삭제에 실패했습니다: {exc}")
        st.divider()
