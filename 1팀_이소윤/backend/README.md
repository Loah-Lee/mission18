# 백엔드 안내

이 폴더는 영화 리뷰 감성 분석 서비스의 FastAPI 백엔드입니다.

## 로컬 실행

```bash
uvicorn app.main:app --reload
```

## 데이터베이스 동작 방식

- 기본값으로는 backend 폴더 안의 `movies.db`를 사용합니다.
- `DATABASE_PATH` 환경변수를 지정하면 해당 경로의 DB 파일을 사용합니다.
- `DATABASE_PATH`가 새 파일을 가리키고, 기본 `movies.db`가 존재하면 첫 실행 시 기본 DB를 복사해서 사용합니다.

예시:

```bash
DATABASE_PATH=/var/data/movies.db
```

이 프로젝트는 현재 로컬 백엔드 실행 기준으로 검증하는 흐름을 기준으로 정리했습니다.
