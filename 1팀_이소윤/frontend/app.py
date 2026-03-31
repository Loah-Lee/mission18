import streamlit as st

from api_client import BACKEND_BASE_URL, get_health

st.set_page_config(page_title="영화 리뷰 감성 분석", layout="wide")

st.title("영화 리뷰 감성 분석")
st.write("영화 정보, 리뷰, 감성 분석 결과를 확인하는 Streamlit 프론트엔드입니다.")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("사용 방법")
    st.markdown(
        """
        1. 사이드바의 `영화` 페이지에서 영화를 등록합니다.
        2. `리뷰` 페이지에서 영화별 리뷰를 작성합니다.
        3. 영화별 리뷰 목록과 감성 분석 점수를 확인합니다.
        """
    )

with col2:
    st.subheader("백엔드 상태")
    st.caption(f"Base URL: `{BACKEND_BASE_URL}`")
    try:
        health = get_health()
        st.success(f"연결됨: {health['status']}")
    except Exception as exc:
        st.error(f"백엔드 연결 실패: {exc}")

st.info("사이드바의 `영화`, `리뷰` 페이지에서 데이터를 관리하세요.")
