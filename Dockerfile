# ============================================
# ЭТАП 1: Сборка зависимостей
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .

# Устанавливаем зависимости В ГЛОБАЛЬНУЮ ПАПКУ
RUN pip install --no-cache-dir -r requirements.txt

# ============================================
# ЭТАП 2: Финальный образ
# ============================================
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем ВСЕ установленные пакеты из builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем приложение и файлы
COPY app/ ./app/
COPY alembic.ini .
COPY migrations/ ./migrations/
COPY app/startup.sh .

RUN chmod +x startup.sh

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["./startup.sh"]