from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import logging
import os
from datetime import datetime

from .database import init_db, get_db, SessionLocal
from .models import Base, Visit
from .cache import (
    init_redis, get_cached_counter, set_cached_counter,
    get_cached_static, set_cached_static
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация БД и Redis при старте
def startup():
    logger.info("Starting application...")
    
    # Инициализация БД
    if not init_db():
        logger.error("Failed to initialize database")
        raise RuntimeError("Database initialization failed")
    
    # Создание таблиц
    from .database import engine
    Base.metadata.create_all(bind=engine)
    
    # Инициализация Redis
    if not init_redis():
        logger.warning("Failed to initialize Redis, continuing without cache")
    
    logger.info("Application started successfully")

# Выполняем инициализацию
startup()

app = FastAPI(title="Visit Counter App", version="1.0.0")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Главная страница с счетчиком посещений"""
    try:
        # Пытаемся получить счетчик из кэша
        counter = get_cached_counter()
        
        if counter is None:
            # Если в кэше нет, берем из БД
            visit = db.query(Visit).first()
            if visit:
                counter = visit.counter
                # Обновляем счетчик в БД
                visit.counter += 1
                visit.last_visit = datetime.utcnow()
            else:
                # Создаем первую запись
                visit = Visit(counter=1, last_visit=datetime.utcnow())
                db.add(visit)
                counter = 1
            
            db.commit()
            
            # Сохраняем в кэш
            set_cached_counter(counter)
        else:
            # Обновляем счетчик в БД
            visit = db.query(Visit).first()
            if visit:
                visit.counter = counter + 1
                visit.last_visit = datetime.utcnow()
            else:
                visit = Visit(counter=counter + 1, last_visit=datetime.utcnow())
                db.add(visit)
            
            db.commit()
            counter += 1
            
            # Обновляем кэш
            set_cached_counter(counter)
        
        # Кэшируем статику (пример)
        static_data = get_cached_static("index")
        if static_data is None:
            static_data = {
                "title": "Visit Counter",
                "description": "Simple visit counter application",
                "version": "1.0.0"
            }
            set_cached_static("index", static_data)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{static_data['title']}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 50px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                    width: 100%;
                }}
                h1 {{
                    color: #333;
                    margin-bottom: 20px;
                }}
                .counter {{
                    font-size: 72px;
                    font-weight: bold;
                    color: #667eea;
                    margin: 20px 0;
                }}
                .info {{
                    color: #666;
                    margin-top: 20px;
                    font-size: 14px;
                }}
                .badge {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 12px;
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{static_data['description']}</h1>
                <div class="counter">{counter}</div>
                <p>Total visits</p>
                <div class="badge">Version {static_data['version']}</div>
                <div class="info">
                    <p>User Agent: {request.headers.get('user-agent', 'Unknown')}</p>
                    <p>Cache: {'Enabled' if get_cached_counter() is not None else 'Disabled'}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return HTMLResponse(f"<h1>Error</h1><p>{str(e)}</p>", status_code=500)

@app.get("/health")
async def health():
    """Endpoint для проверки здоровья приложения"""
    return {"status": "healthy"}

@app.get("/stats")
async def stats(db: Session = Depends(get_db)):
    """Статистика посещений"""
    visit = db.query(Visit).first()
    if visit:
        return {
            "total_visits": visit.counter,
            "last_visit": visit.last_visit.isoformat() if visit.last_visit else None
        }
    return {"total_visits": 0, "last_visit": None}