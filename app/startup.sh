#!/bin/bash
set -e

echo "=== Запуск миграций Alembic ==="
alembic upgrade head

echo "=== Запуск приложения ==="
uvicorn app.main:app --host 0.0.0.0 --port 8000