# 배포 가이드

## 1. Render에 백엔드 배포

리포지토리 루트에 있는 `render.yaml`을 사용하면 Render Blueprint 방식으로 바로 배포할 수 있습니다.

- 설정 파일: `render.yaml`
- 서비스 이름: `mission18-backend`
- 루트 디렉터리: `1팀_이소윤/backend`

Blueprint를 쓰지 않고 Render에서 직접 설정해도 됩니다. 그 경우 값은 아래와 같습니다.

- Runtime: `Python`
- Root Directory: `1팀_이소윤/backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 데이터베이스 관련

- 기본적으로 백엔드는 `1팀_이소윤/backend/movies.db`를 읽습니다.
- 현재 리포지토리에 `movies.db`가 포함되어 있으므로, 첫 배포 시점에는 지금까지 저장한 영화와 리뷰 데이터를 그대로 사용할 수 있습니다.
- 이후 더 안정적으로 데이터를 유지하려면 `DATABASE_PATH`를 별도 경로로 지정하고, Render Persistent Disk를 붙이는 방식이 좋습니다.

예시:

```bash
DATABASE_PATH=/var/data/movies.db
```

## 2. Streamlit Cloud 설정

프론트엔드는 아래 파일을 기준으로 배포합니다.

- 앱 파일: `1팀_이소윤/frontend/app.py`

Streamlit Cloud에서는 아래 둘 중 하나로 `BACKEND_BASE_URL`을 설정하면 됩니다.

- Environment Variable
- Secrets

예시:

```toml
BACKEND_BASE_URL = "https://your-render-backend-url.onrender.com"
```

주의:

- `BACKEND_BASE_URL`에는 `Streamlit 앱 주소`가 아니라 `배포된 FastAPI 주소`를 넣어야 합니다.
- 예를 들어 `https://mission18-codeit-loah.streamlit.app`를 넣으면 안 됩니다.

## 3. 연결 구조

- Streamlit 프론트 주소 예시:
  - `https://mission18-codeit-loah.streamlit.app`
- FastAPI 백엔드 주소 예시:
  - `https://mission18-backend.onrender.com`

정상 구조는 아래와 같습니다.

- 사용자 -> Streamlit -> FastAPI -> SQLite

즉 Streamlit은 반드시 자기 자신이 아니라 FastAPI 백엔드를 호출해야 합니다.
