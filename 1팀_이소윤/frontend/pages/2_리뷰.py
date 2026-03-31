import streamlit as st

from api_client import create_review, delete_review, get_movie_reviews, get_movies

st.title("리뷰")
st.caption("리뷰를 작성하면 감성 분석이 자동 실행되고, 영화별 리뷰 목록을 확인할 수 있습니다.")

try:
    movies = get_movies()
except Exception as exc:
    st.error(f"영화 목록을 불러오지 못했습니다: {exc}")
    movies = []

movie_lookup = {movie["id"]: movie["title"] for movie in movies}
movie_options = {
    f"{movie['title']} ({movie['release_date']})": movie["id"]
    for movie in movies
}

st.subheader("리뷰 추가")

if not movie_options:
    st.info("먼저 영화 페이지에서 영화를 한 편 이상 등록하세요.")
else:
    with st.form("create_review_form", clear_on_submit=True):
        selected_movie_label = st.selectbox("영화", options=list(movie_options.keys()))
        author = st.text_input("작성자")
        content = st.text_area("리뷰 내용", height=160)
        submitted = st.form_submit_button("리뷰 저장")

        if submitted:
            if not author or not content.strip():
                st.warning("작성자와 리뷰 내용을 모두 입력하세요.")
            else:
                payload = {
                    "movie_id": movie_options[selected_movie_label],
                    "author": author,
                    "content": content,
                }
                try:
                    created = create_review(payload)
                    st.success(
                        f"리뷰가 저장되었습니다. 감성 분석 결과: {created['sentiment_label']} ({created['sentiment_score']})"
                    )
                except Exception as exc:
                    st.error(f"리뷰 저장에 실패했습니다: {exc}")

st.divider()
st.subheader("영화별 리뷰 목록")

if not movies:
    st.info("아직 저장된 영화가 없습니다.")
else:
    for movie in movies:
        try:
            movie_reviews = get_movie_reviews(movie["id"])
        except Exception as exc:
            st.error(f"{movie['title']}의 리뷰를 불러오지 못했습니다: {exc}")
            movie_reviews = []

        with st.expander(f"{movie['title']} 리뷰 {len(movie_reviews)}개", expanded=True):
            if not movie_reviews:
                st.info("아직 등록된 리뷰가 없습니다.")
                continue

            for review in movie_reviews:
                st.markdown(f"### 리뷰 #{review['id']}")
                st.write(f"영화: {movie['title']}")
                st.write(f"등록일: {review['created_at']}")
                st.write(f"작성자: {review['author']}")
                st.write(f"리뷰 내용: {review['content']}")
                st.write(
                    f"감성 분석 결과: {review['sentiment_label']} ({review['sentiment_score']})"
                )
                if st.button("리뷰 삭제", key=f"delete_review_{review['id']}"):
                    try:
                        delete_review(review["id"])
                        st.success(f"리뷰 #{review['id']}를 삭제했습니다.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"리뷰 삭제에 실패했습니다: {exc}")
                st.divider()
