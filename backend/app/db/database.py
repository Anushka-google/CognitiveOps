from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from dotenv import load_dotenv
import os


# ==========================================
# Environment Configuration
# ==========================================

load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL"
)


# ==========================================
# Database Engine
# ==========================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800
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