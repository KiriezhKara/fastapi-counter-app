#!/bin/bash

echo "========================================="
echo "  СИМУЛЯЦИЯ ОТКАЗА БАЗЫ ДАННЫХ"
echo "========================================="
echo ""

echo "📊 Текущий статус контейнеров:"
docker ps --format "table {{.Names}}\t{{.Status}}"
echo ""

echo "📊 Текущий счетчик:"
curl -s http://localhost:8000/stats 2>/dev/null | python -m json.tool || echo "Приложение недоступно"
echo ""

echo "🛑 Останавливаем PostgreSQL на 10 секунд..."
docker stop fastapi-postgres
echo "✅ PostgreSQL остановлен"
echo ""

echo "⏳ Ждем 10 секунд..."
for i in {10..1}; do
    echo -n "$i... "
    sleep 1
done
echo ""
echo ""

echo "✅ Запускаем PostgreSQL..."
docker start fastapi-postgres
echo "✅ PostgreSQL запущен"
echo ""

echo "⏳ Ждем восстановления соединения (15 секунд)..."
sleep 15

echo ""
echo "📊 Статус контейнеров после восстановления:"
docker ps --format "table {{.Names}}\t{{.Status}}"
echo ""

echo "📊 Проверяем, что приложение восстановило соединение:"
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)
echo "Healthcheck: $HEALTH"
echo ""

echo "📊 Проверяем счетчик:"
curl -s http://localhost:8000/stats 2>/dev/null | python -m json.tool
echo ""

echo "📊 Делаем новый запрос к главной странице:"
curl -s http://localhost:8000/ 2>/dev/null | grep -o '<div class="counter">[0-9]*</div>' || echo "Приложение недоступно"
echo ""

echo "========================================="
echo "  ТЕСТ ЗАВЕРШЕН"
echo "========================================="