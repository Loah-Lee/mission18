# 1팀_이소윤 프로젝트 안내

이 폴더는 미션 18 제출용 영화 리뷰 감성 분석 프로젝트입니다.

## 전체 구조

- `frontend/`
  - Streamlit 프론트엔드
  - 영화 등록/수정/삭제, 리뷰 등록/조회/삭제, 평균 평점 시각화 제공
- `backend/`
  - FastAPI 백엔드
  - 영화/리뷰 API, 감성 분석, SQLite 저장 담당
- `docs/`
  - 보고서 초안, 구조도, ERD, FastAPI Docs 캡처, 서비스 동작 캡처
- `report.pdf`
  - 제출용 보고서 PDF

## 동작 흐름

1. 사용자가 Streamlit 화면에서 영화를 등록한다.
2. Streamlit이 FastAPI 백엔드로 영화 데이터를 전송한다.
3. 사용자가 리뷰를 등록하면 FastAPI가 감성 분석 모델을 실행한다.
4. 감성 분석 결과와 리뷰가 SQLite DB에 저장된다.
5. 프론트엔드에서 영화별 평균 평점과 감성 분포를 시각화해서 보여준다.

## 주요 파일

- 프론트엔드 시작점: `frontend/app.py`
- 영화 페이지: `frontend/pages/1_영화.py`
- 리뷰 페이지: `frontend/pages/2_리뷰.py`
- 백엔드 시작점: `backend/app/main.py`
- DB 설정: `backend/app/database.py`
- 감성 분석: `backend/app/services/sentiment.py`

## 로컬 실행

### 백엔드

```bash
cd 1팀_이소윤/backend
uvicorn app.main:app --reload
```

### 프론트엔드

```bash
cd 1팀_이소윤/frontend
streamlit run app.py
```

## 배포 흐름

1. 로컬에서 FastAPI 백엔드를 실행해 기능을 검증한다.
2. Streamlit Cloud에는 프론트엔드만 배포한다.
3. 제출용 캡처와 보고서는 로컬 실행 기준 결과를 사용한다.
