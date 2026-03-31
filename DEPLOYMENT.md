# Deployment Guide

## 1. Backend deploy on Render

Use the repository root blueprint file:

- File: `render.yaml`
- Service name: `mission18-backend`
- Root directory: `1팀_이소윤/backend`

If you deploy manually on Render instead of using Blueprint:

- Runtime: Python
- Root Directory: `1팀_이소윤/backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Important

- The repo includes `1팀_이소윤/backend/movies.db`, so the first deploy starts with the current movie and review data.
- For longer-lived demo data, set `DATABASE_PATH` to a persistent location if you later attach a disk.

## 2. Streamlit Cloud settings

Deploy the frontend from:

- App file: `1팀_이소윤/frontend/app.py`

In Streamlit Cloud, set either:

- Environment variable: `BACKEND_BASE_URL`
- Or Secret:

```toml
BACKEND_BASE_URL = "https://your-render-backend-url.onrender.com"
```

Do not set `BACKEND_BASE_URL` to the Streamlit app URL.

## 3. Expected wiring

- Streamlit frontend URL:
  - Example: `https://mission18-codeit-loah.streamlit.app`
- FastAPI backend URL:
  - Example: `https://mission18-backend.onrender.com`

The frontend must call the backend URL, not itself.
