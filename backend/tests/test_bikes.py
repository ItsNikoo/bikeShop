import pytest
from httpx import AsyncClient

from repositories.bike_repository import BikeRepository
from schemas import BikeCreate, BikeUpdate


async def create_brand(client: AsyncClient):
    data = {
        "name": "Corratec",
        "description": "desc",
        "country": "Germany"
    }
    await client.post("/brands", json=data)


@pytest.mark.asyncio
class TestBikeCreate:
    """Тесты POST-запросов велосипедов"""

    async def test_bike_create_failure_invalid_year(self, client: AsyncClient):
        invalid_year_bike_data = {
            "brand_id": 1,
            "model": "Navigator",
            "year": 1999,
            "description": "desc"
        }
        response = await client.post("/bikes", json=invalid_year_bike_data)
        assert response.status_code == 422
        assert "detail" in response.json()

    async def test_bike_create_failure_invalid_brand(self, client: AsyncClient):
        invalid_brand_bike_data = {
            "brand_id": 0,
            "model": "Navigator",
            "year": 2025,
            "description": "desc"
        }
        response = await client.post("/bikes", json=invalid_brand_bike_data)
        assert response.status_code == 404
        assert "detail" in response.json()

    async def test_bike_create_failure_field_required(self, client: AsyncClient):
        invalid_data = {
            "brand_id": 1,
            "year": 2025,
            "description": "desc"
        }
        await create_brand(client)
        response = await client.post("/bikes", json=invalid_data)
        assert response.status_code == 422
        assert "detail" in response.json()

    async def test_bike_create_success(self, client: AsyncClient):
        valid_brand_bike_data = {
            "brand_id": 1,
            "model": "Vert Motion",
            "year": 2025,
            "description": "Corratec Vert Motion"
        }
        await create_brand(client)
        response = await client.post("/bikes", json=valid_brand_bike_data)
        assert response.status_code == 201
        data = response.json()
        assert data["brand_id"] == 1
        assert data["model"] == "Vert Motion"
        assert data["year"] == 2025
        assert data["description"] == "Corratec Vert Motion"


@pytest.mark.asyncio
class TestBikeRead:
    """Тесты GET-запросов велосипедов"""

    @staticmethod
    async def fill_db(client: AsyncClient):
        data = {
            "name": "Corratec",
            "description": "desc",
            "country": "Germany"
        }
        await client.post("/brands", json=data)
        bikes_data = [
            {
                "brand_id": 1,
                "model": "Vert Motion",
                "year": 2025,
                "description": "Corratec Vert Motion"
            },
            {
                "brand_id": 1,
                "model": "Vert Expert",
                "year": 2025,
                "description": "Corratec Vert Expert"
            }
        ]
        for bike in bikes_data:
            response = await client.post("/bikes", json=bike)
            assert response.status_code == 201

    async def test_bike_read(self, client: AsyncClient):
        await self.fill_db(client)
        response = await client.get("/bikes")
        assert response.status_code == 200
        assert len(response.json()) == 2

    async def test_get_bike_by_id_success(self, client: AsyncClient):
        await create_brand(client)
        await client.post("/bikes", json={"brand_id": 1, "model": "Test", "year": 2025})

        response = await client.get("/bikes/1")
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "Test"
        assert data["brand_id"] == 1

    async def test_get_bike_by_id_failure(self, client: AsyncClient):
        response = await client.get("/bikes/999")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestBikeUpdate:
    """Тесты для PATCH-запросов велосипедов"""
    async def test_patch_bike_success_full_update(self, client: AsyncClient):
        # Сначала создаём бренд и велосипед
        await create_brand(client)  # Corratec, id=1
        await client.post("/bikes", json={"brand_id": 1, "model": "Old", "year": 2020})

        # Создаём второй бренд для смены
        await client.post("/brands", json={"name": "Stels", "description": "abracadabra", "country": "Russia"})

        update_data = {
            "brand_id": 2,  # меняем бренд
            "model": "New Model",
            "year": 2025,
            "description": "Новое описание"
        }
        response = await client.patch("/bikes/1", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["brand_id"] == 2
        assert data["model"] == "New Model"
        assert data["year"] == 2025

    async def test_patch_bike_success_partial_update(self, client: AsyncClient):
        await create_brand(client)
        await client.post("/bikes", json={"brand_id": 1, "model": "Old", "year": 2020, "description": "Старое"})

        response = await client.patch("/bikes/1", json={"model": "Новый модель"})

        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "Новый модель"
        assert data["year"] == 2020  # не изменился
        assert data["description"] == "Старое"  # не изменился

    async def test_patch_bike_failure_invalid_brand(self, client: AsyncClient):
        await create_brand(client)
        create_resp = await client.post("/bikes", json={"brand_id": 1, "model": "Test", "year": 2025})
        bike_id = create_resp.json()["id"]

        response = await client.patch(f"/bikes/{bike_id}", json={"brand_id": 999})

        assert response.status_code == 404
        assert "Бренд с ID 999 не найден" in response.json()["detail"]

    async def test_patch_bike_failure_invalid_year(self, client: AsyncClient):
        await create_brand(client)
        create_resp = await client.post("/bikes", json={"brand_id": 1, "model": "Test", "year": 2025})
        bike_id = create_resp.json()["id"]

        response = await client.patch(f"/bikes/{bike_id}", json={"year": 1900})

        assert response.status_code == 422  # валидация Pydantic


@pytest.mark.asyncio
class TestBikeDelete:
    """Тесты для DELETE-запросов велосипедов"""
    async def test_delete_bike_success(self, client: AsyncClient):
        await create_brand(client)
        await client.post("/bikes", json={"brand_id": 1, "model": "ToDelete", "year": 2025})

        response = await client.delete("/bikes/1")

        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # Проверяем, что велосипед правда удалён
        get_resp = await client.get("/bikes/1")
        assert get_resp.status_code == 404

    async def test_delete_bike_failure_not_found(self, client: AsyncClient):
        response = await client.delete("/bikes/999")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestBikeRepository:
    """Тестирование репозитория велосипедов напрямую"""

    async def test_repository_create(self, db_session):
        repository = BikeRepository(db_session)

        # Предполагаем, что бренд с id=1 уже существует (создаётся в фикстурах или вручную)
        # Если нет — можно добавить создание бренда здесь, но обычно это в фикстурах
        bike_data = BikeCreate(
            brand_id=1,
            model="Navigator 500",
            year=2024,
            description="Классический горный велосипед"
        )

        bike = await repository.create(bike_data)

        assert bike.id is not None
        assert bike.brand_id == 1
        assert bike.model == "Navigator 500"
        assert bike.year == 2024
        assert bike.description == "Классический горный велосипед"

    @staticmethod
    async def fill_db(db_session):
        repository = BikeRepository(db_session)
        bikes_data = [
            BikeCreate(brand_id=1, model="Vert Motion", year=2025, description="Corratec Vert Motion"),
            BikeCreate(brand_id=1, model="Riot Pro", year=2024, description="Outleap Riot Pro"),
            BikeCreate(brand_id=1, model="Wireguard", year=2023),
        ]
        for bike in bikes_data:
            await repository.create(bike)

    async def test_repository_get_all(self, db_session):
        repository = BikeRepository(db_session)
        await self.fill_db(db_session)

        bikes = await repository.get_all()
        assert len(bikes) == 3

        models = {b.model for b in bikes}
        assert models == {"Vert Motion", "Riot Pro", "Wireguard"}

    async def test_repository_get_by_id(self, db_session):
        repository = BikeRepository(db_session)
        await self.fill_db(db_session)

        bike = await repository.get_by_id(1)
        assert bike is not None
        assert bike.id == 1
        assert bike.model == "Vert Motion"
        assert bike.year == 2025
        assert bike.description == "Corratec Vert Motion"

    async def test_repository_get_by_id_not_found(self, db_session):
        repo = BikeRepository(db_session)
        result = await repo.get_by_id(999)
        assert result is None

    async def test_repository_delete_success(self, db_session):
        repository = BikeRepository(db_session)
        await self.fill_db(db_session)

        bikes_before = await repository.get_all()
        assert len(bikes_before) == 3

        result = await repository.delete(2)  # удаляем второй велосипед (Riot Pro)
        assert result == {"status": "success"}

        bikes_after = await repository.get_all()
        assert len(bikes_after) == 2
        models = {b.model for b in bikes_after}
        assert "Riot Pro" not in models

    async def test_repository_delete_not_found(self, db_session):
        repo = BikeRepository(db_session)
        await self.fill_db(db_session)

        result = await repo.delete(999)
        assert result is None

        # Данные не пострадали
        bikes = await repo.get_all()
        assert len(bikes) == 3

    async def test_repository_patch_success_full(self, db_session):
        repository = BikeRepository(db_session)
        await self.fill_db(db_session)

        original = await repository.get_by_id(1)
        assert original.model == "Vert Motion"
        assert original.year == 2025

        update_data = BikeUpdate(
            model="Vert Motion Pro",
            year=2025,
            description="Обновлённая версия",
            brand_id=1  # можно оставить или изменить, если есть другой бренд
        )

        updated = await repository.patch(1, update_data)

        assert updated is not None
        assert updated.id == 1
        assert updated.model == "Vert Motion Pro"
        assert updated.year == 2025
        assert updated.description == "Обновлённая версия"

    async def test_repository_patch_partial_update(self, db_session):
        repository = BikeRepository(db_session)

        # Создаём один велосипед с полными данными
        full_bike = BikeCreate(
            brand_id=1,
            model="Original Model",
            year=2023,
            description="Старое описание"
        )
        created = await repository.create(full_bike)

        assert created.model == "Original Model"
        assert created.description == "Старое описание"
        assert created.year == 2023

        # Частичное обновление — только модель
        partial_update = BikeUpdate(model="Новый крутой модель")

        updated = await repository.patch(created.id, partial_update)

        assert updated is not None
        assert updated.id == created.id
        assert updated.model == "Новый крутой модель"
        assert updated.year == 2023  # не изменилось
        assert updated.description == "Старое описание"  # не изменилось
        assert updated.brand_id == 1  # не изменилось

    async def test_repository_patch_not_found(self, db_session):
        repository = BikeRepository(db_session)
        await self.fill_db(db_session)

        update_data = BikeUpdate(model="Не найдёт")

        result = await repository.patch(500, update_data)
        assert result is None

        # База не изменилась
        bikes = await repository.get_all()
        assert len(bikes) == 3