# FastAPI Visit Counter Application

Простое веб-приложение на FastAPI, которое считает количество посещений страницы с сохранением в PostgreSQL и кэшированием в Redis.

## Технологический стек

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions

## Функциональность

- ✅ Счетчик посещений страницы
- ✅ Сохранение в PostgreSQL
- ✅ Кэширование в Redis
- ✅ Healthcheck для БД
- ✅ Сетевой мост между сервисами
- ✅ Adminer для управления БД
- ✅ Redis Commander для просмотра кэша
- ✅ Профили для dev/prod окружений

## Запуск

### Разработка (с Adminer и Redis Commander)
```bash
docker-compose --profile dev up -d