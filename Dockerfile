# ============================================
# ЭТАП 1: Сборка зависимостей
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Устанавливаем только gcc для сборки (без postgresql-client)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .

# Устанавливаем зависимости в отдельную папку
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================
# ЭТАП 2: Финальный образ
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем только runtime зависимости (без gcc)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем установленные пакеты из builder
COPY --from=builder /root/.local /root/.local

# Копируем приложение и файлы
COPY app/ ./app/
COPY alembic.ini .
COPY migrations/ ./migrations/
COPY app/startup.sh .

RUN chmod +x startup.sh

# Создаем пользователя
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Добавляем пути
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["./startup.sh"]