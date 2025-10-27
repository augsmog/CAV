"""
Database models and connection management for CAV Model
"""

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import get_config

# Base class for all models
Base = declarative_base()

# Global session maker
_SessionLocal = None
_engine = None


def get_engine():
    """Get or create database engine"""
    global _engine
    
    if _engine is None:
        config = get_config()
        db_type = config.db_type
        
        if db_type == 'sqlite':
            db_path = Path(config.db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            database_url = f"sqlite:///{db_path}"
            _engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
        elif db_type == 'postgresql':
            host = config.get('database.postgresql.host')
            port = config.get('database.postgresql.port')
            database = config.get('database.postgresql.database')
            user = config.get('database.postgresql.user')
            password = config.get('database.postgresql.password')
            
            database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            _engine = create_engine(database_url, echo=False)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _engine


def get_session_maker():
    """Get or create session maker"""
    global _SessionLocal
    
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return _SessionLocal


def get_session():
    """Get a new database session"""
    SessionLocal = get_session_maker()
    return SessionLocal()


def init_database():
    """Initialize database with all tables"""
    from database.models import (
        Player, Team, PerformanceStat, Transfer, 
        SocialMedia, NILDeal, Injury, SchemeInfo
    )
    
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database initialized at: {get_config().db_path}")


def close_connections():
    """Close all database connections"""
    global _engine, _SessionLocal
    
    if _engine:
        _engine.dispose()
        _engine = None
    
    _SessionLocal = None

