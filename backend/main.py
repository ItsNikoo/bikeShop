from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import create_tables, engine
from routers.bike_router import router as bike_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    print("Создание базы данных.")
    yield
    # Shutdown
    await engine.dispose()
    print("Соединения с бд закрыты")


app = FastAPI(lifespan=lifespan)


app.include_router(bike_router)
