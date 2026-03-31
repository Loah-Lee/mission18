# 백엔드 안내

이 폴더는 영화 리뷰 감성 분석 서비스의 FastAPI 백엔드입니다.

## 로컬 실행

```bash
uvicorn app.main:app --reload
```

## Render 배포

이 백엔드는 Render의 Python Web Service로 배포할 수 있습니다.

- 루트 디렉터리: `1팀_이소윤/backend`
- 빌드 명령어: `pip install -r requirements.txt`
- 시작 명령어: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 데이터베이스 동작 방식

- 기본값으로는 backend 폴더 안의 `movies.db`를 사용합니다.
- 현재 리포지토리에 `movies.db`가 포함되어 있으므로, 처음 배포할 때는 지금 저장된 영화/리뷰 데이터가 함께 올라갑니다.
- `DATABASE_PATH` 환경변수를 지정하면 해당 경로의 DB 파일을 사용합니다.
- `DATABASE_PATH`가 새 파일을 가리키고, 기본 `movies.db`가 존재하면 첫 실행 시 기본 DB를 복사해서 사용합니다.

예시:

```bash
DATABASE_PATH=/var/data/movies.db
```

이 방식은 나중에 Render Persistent Disk를 연결할 때 유용합니다.
