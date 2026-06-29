from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import time
import os
import logging

logger = logging.getLogger(__name__)

# Получение параметров подключения из переменных окружения
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "counter_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = None
SessionLocal = None

def init_db():
    """Инициализация подключения к БД с повторными попытками"""
    global engine, SessionLocal
    
    max_retries = 30
    retry_interval = 2
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            
            # Проверка подключения
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info(f"Successfully connected to database on attempt {attempt + 1}")
            return True
            
        except OperationalError as e:
            logger.warning(f"Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
            time.sleep(retry_interval)
    
    logger.error("Failed to connect to database after all retries")
    return False

def get_db():
    """Генератор для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()