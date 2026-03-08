import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from cache import redis

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db_test"

engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
async def prepare_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(autouse=True)
async def clean():
    await redis.flushdb()
    async with engine.begin() as conn:
        await conn.execute(Base.metadata.tables["posts"].delete())
    yield


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def test_get_post_puts_in_cache(client):
    """GET /posts/{id} кладёт пост в Redis"""
    r = await client.post("/posts/", json={"title": "Test", "content": "Hello"})
    post_id = r.json()["id"]

    assert await redis.get(f"post:{post_id}") is None

    await client.get(f"/posts/{post_id}")

    assert await redis.get(f"post:{post_id}") is not None


async def test_update_invalidates_cache(client):
    """PUT /posts/{id} удаляет пост из кеша"""
    r = await client.post("/posts/", json={"title": "Old", "content": "Old"})
    post_id = r.json()["id"]

    await client.get(f"/posts/{post_id}")
    assert await redis.get(f"post:{post_id}") is not None

    await client.put(f"/posts/{post_id}", json={"title": "New", "content": "New"})

    assert await redis.get(f"post:{post_id}") is None


async def test_delete_invalidates_cache(client):
    """DELETE /posts/{id} удаляет пост из кеша"""
    r = await client.post("/posts/", json={"title": "ToDelete", "content": "Bye"})
    post_id = r.json()["id"]

    await client.get(f"/posts/{post_id}")
    assert await redis.get(f"post:{post_id}") is not None

    await client.delete(f"/posts/{post_id}")

    assert await redis.get(f"post:{post_id}") is None
