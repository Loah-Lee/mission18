# Backend

FastAPI backend for the movie review sentiment mission.

## Local run

```bash
uvicorn app.main:app --reload
```

## Render deployment

This backend can be deployed as a Python Web Service on Render.

- Root directory: `1팀_이소윤/backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Database behavior

- By default, the app reads `movies.db` in the backend directory.
- The repository already includes `movies.db`, so the initial deployed service will start with the current seeded movie and review data.
- If you set `DATABASE_PATH`, the app will use that path instead.
- When `DATABASE_PATH` points to a new file and the bundled `movies.db` exists, the app copies the bundled DB into the new path on first startup.

Example:

```bash
DATABASE_PATH=/var/data/movies.db
```

This is useful if you later attach a persistent disk on Render.
