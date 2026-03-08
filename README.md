# Blog API with Caching

REST API для блога с кешированием популярных постов на Redis.

## Стек

- FastAPI
- PostgreSQL + SQLAlchemy (async)
- Redis
- Alembic
- pytest

## Требования

- Python 3.11+
- Docker

## Установка

### 1. Клонировать репозиторий
```bash
git clone https://github.com/ВАШ_ЮЗЕРНЕЙМ/НАЗВАНИЕ_РЕПО.git
cd НАЗВАНИЕ_РЕПО
```

### 2. Создать виртуальное окружение
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

### 4. Настроить переменные окружения

Скопировать `.env.example` в `.env`:
```bash
cp .env.example .env          # Mac/Linux
copy .env.example .env        # Windows
```

Заполнить `.env` своими значениями:
```ini
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/test_db
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/test_db_test
REDIS_URL=redis://localhost:6379
```

### 5. Запустить PostgreSQL и Redis
```bash
docker-compose up -d
```

Остановить:
```bash
docker-compose down
```

### 6. Применить миграции
```bash
alembic upgrade head
```

### 7. Запустить сервер
```bash
uvicorn main:app --reload
```

Документация: http://localhost:8000/docs

## Тесты

Создать тестовую БД:
```bash
psql -U postgres -c "CREATE DATABASE test_db_test;"
```

Запустить тесты:
```bash
pytest tests/ -v
```

## Эндпоинты

| Метод  | URL           | Описание            |
|--------|---------------|---------------------|
| POST   | /posts/       | Создать пост        |
| GET    | /posts/       | Получить все посты  |
| GET    | /posts/{id}   | Получить пост по ID |
| PUT    | /posts/{id}   | Обновить пост       |
| DELETE | /posts/{id}   | Удалить пост        |

## Логика кеширования

- `GET /posts/{id}` — проверяет Redis, если нет — берёт из PostgreSQL и кладёт в кеш
- `PUT /posts/{id}` — обновляет пост и инвалидирует кеш
- `DELETE /posts/{id}` — удаляет пост и инвалидирует кеш