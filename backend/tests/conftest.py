import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from models import Model
from dependencies import get_db

# Создаем тестовый движок для in-memory базы данных
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
)

# Создаем фабрику сессий для тестов
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Переопределяем зависимость get_db для тестов
async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function", autouse=False)
async def setup_database():
    """Создание и очистка тестовой базы данных для каждого теста"""
    # Создаем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

    yield

    # Удаляем таблицы после теста
    async with test_engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)

    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_database):
    """Фикстура для получения сессии базы данных в тестах"""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(setup_database):
    """Фикстура для HTTP клиента с переопределенной зависимостью БД"""
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as ac:
        yield ac

    # Очищаем переопределения после теста
    app.dependency_overrides.clear()
