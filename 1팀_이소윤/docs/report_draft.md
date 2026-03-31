# 영화 리뷰 감성 분석 서비스 보고서 초안

## 1. 서비스 개요
- 서비스명: 영화 리뷰 감성 분석 웹 애플리케이션
- 목표: 영화 정보, 사용자 리뷰, 감성 분석 결과를 한 화면에서 확인할 수 있는 웹 서비스를 구현한다.
- 기술 스택:
  - 프론트엔드: Streamlit
  - 백엔드: FastAPI
  - 데이터베이스: SQLite
  - 감성 분석: Hugging Face `monologg/koelectra-small-finetuned-sentiment`

## 2. 서비스 구조도
- 사용자 -> Streamlit -> FastAPI -> SQLite
- 리뷰 등록 시 FastAPI -> Hugging Face 감성 분석 모델 -> 결과 저장
- 보고서 PDF에는 구조도 이미지를 함께 삽입한다.

## 3. 프론트엔드 구현 내용
- 영화 등록
  - 제목, 한국 개봉일, 감독, 장르, 포스터 URL 입력 가능
- 영화 목록 조회
  - 영화 포스터, 제목, 감독, 장르, 평균 평점, 리뷰 수 표시
- 영화 수정 및 삭제
  - 등록된 영화 정보를 수정할 수 있고 삭제할 수 있음
- 평균 평점 시각화
  - 영화별 평균 평점 막대 그래프 제공
  - 각 영화별 긍정/중립/부정 리뷰 분포 시각화 제공
- 리뷰 등록
  - 영화 선택 후 작성자, 리뷰 내용 입력 가능
- 리뷰 조회 및 삭제
  - 영화별 리뷰 목록 확인 가능
  - 등록된 리뷰 삭제 가능

## 4. 백엔드 구현 내용
- 영화 관리 API
  - 영화 등록, 전체 조회, 상세 조회, 수정, 삭제
- 리뷰 관리 API
  - 리뷰 등록, 전체 조회, 영화별 조회, 삭제
- 평점 API
  - 영화별 감성 점수 평균 조회
- 감성 분석 처리
  - 리뷰 등록 시 자동으로 감성 분석 수행
  - 분석 결과를 `positive`, `neutral`, `negative`와 1~5점 점수로 저장

## 5. 모델 선택 및 경량화 고려
- 선택 모델: `monologg/koelectra-small-finetuned-sentiment`
- 선택 이유:
  - 한국어 감성 분석에 적합함
  - `small` 계열이라 로컬 환경(M1, 8GB)에서 비교적 가볍게 실행 가능
  - Hugging Face 생태계와 연동이 쉬워 FastAPI에서 바로 활용 가능
- 경량화 관점에서 고려한 점:
  - 작은 모델 선택
  - 앱 실행 후 모델 1회 로드 및 재사용
  - 로컬 CPU 기반 추론으로도 동작 가능하도록 구성
- 추가 보정:
  - 영화 리뷰 특성상 슬픈 감상이나 반어적 표현이 단순 부정으로 오분류되는 경우가 있어 후처리 규칙을 추가함

## 6. 데이터베이스 구조도(ERD)
- `Movie`
  - id, title, release_date, director, genre, poster_url, created_at
- `Review`
  - id, movie_id, author, content, sentiment_label, sentiment_score, created_at
- 관계:
  - Movie 1 : N Review

## 7. API 명세 요약
- `GET /health`
- `POST /movies`
- `GET /movies`
- `GET /movies/{movie_id}`
- `PUT /movies/{movie_id}`
- `DELETE /movies/{movie_id}`
- `GET /movies/{movie_id}/rating`
- `POST /reviews`
- `GET /reviews`
- `GET /movies/{movie_id}/reviews`
- `DELETE /reviews/{review_id}`
- FastAPI Swagger Docs: `http://127.0.0.1:8000/docs`

## 8. 테스트 데이터 요약
- 등록 영화 수: 3편
  - 헤어질 결심
  - 이터널 선샤인
  - 러브레터
- 각 영화별 리뷰 수: 13개
- 평균 평점은 감성 분석 점수 평균으로 계산됨

## 9. 서비스 동작 캡처 항목
- 영화 3개 이상 등록 화면
- 각 영화별 리뷰 10개 이상 등록 화면
- 영화 페이지 평균 평점 그래프 화면
- 리뷰 페이지 영화별 리뷰 목록 화면
- FastAPI Docs 전체 화면

## 10. 배포
- Streamlit Cloud 배포 링크를 추가한다.
- 배포 후 접속 가능한 URL과 간단한 실행 방법을 보고서에 포함한다.

## 11. 제출 전 최종 체크리스트
- 실제 캡처 이미지를 `docs/screenshots/`에 저장
- 구조도 및 ERD 이미지 완성
- FastAPI Docs 전체 캡처 추가
- Streamlit Cloud 배포 링크 반영
- 최종 보고서 PDF 내 이미지 삽입 후 제출
