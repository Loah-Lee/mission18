import os
import shutil
import sqlite3
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "movies.db"
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(DEFAULT_DB_PATH))).expanduser()


def _ensure_database_file():
    if DATABASE_PATH == DEFAULT_DB_PATH:
        return

    if DATABASE_PATH.exists():
        return

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DEFAULT_DB_PATH.exists():
        shutil.copy2(DEFAULT_DB_PATH, DATABASE_PATH)


_ensure_database_file()
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_movies_autoincrement():
    if not DATABASE_PATH.exists():
        return

    with sqlite3.connect(DATABASE_PATH) as conn:
        row = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='movies'"
        ).fetchone()
        if row is None:
            return

        create_sql = row[0] or ""
        if "AUTOINCREMENT" in create_sql.upper():
            return

        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("BEGIN")
        conn.execute(
            """
            CREATE TABLE movies_new (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                release_date DATE NOT NULL,
                director VARCHAR(255) NOT NULL,
                genre VARCHAR(255) NOT NULL,
                poster_url VARCHAR(1000) NOT NULL,
                created_at DATETIME NOT NULL
            )
            """
        )
        conn.execute(
            """
            INSERT INTO movies_new (id, title, release_date, director, genre, poster_url, created_at)
            SELECT id, title, release_date, director, genre, poster_url, created_at
            FROM movies
            ORDER BY id
            """
        )
        conn.execute("DROP TABLE movies")
        conn.execute("ALTER TABLE movies_new RENAME TO movies")
        conn.execute("CREATE INDEX ix_movies_id ON movies (id)")
        conn.commit()
        conn.execute("PRAGMA foreign_keys = ON")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
