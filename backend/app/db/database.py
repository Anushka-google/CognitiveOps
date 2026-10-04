from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from dotenv import load_dotenv
import os


# ==========================================
# Environment Configuration
# ==========================================

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./cognitiveops.db"

# ==========================================
# Database Engine
# ==========================================

# Use short connect timeout so Render doesn't hang for 15 minutes if DB is sleeping
connect_args = {}
if DATABASE_URL.startswith("postgresql"):
    connect_args["connect_timeout"] = 10
elif DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args=connect_args
)


# ==========================================
# Session
# ==========================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==========================================
# Base Model
# ==========================================

Base = declarative_base()


# ==========================================
# FastAPI Database Dependency
# ==========================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()