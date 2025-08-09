"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from app.core.config import settings

# Database URL - fallback to SQLite for development
DATABASE_URL = settings.DATABASE_URL or "sqlite:///./claritycheck.db"

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}  # Only for SQLite
    )
else:
    engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all database tables
    """
    from app.models.analysis import Base
    Base.metadata.create_all(bind=engine)

def init_db():
    """
    Initialize database with tables and sample data if needed
    """
    create_tables()
    print("✅ Database tables created")