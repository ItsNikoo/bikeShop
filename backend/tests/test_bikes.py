import pytest
from httpx import AsyncClient

from repositories.bike_repository import BikeRepository
from schemas import BikeCreate, BikeUpdate


@pytest.mark.asyncio
class TestBikeCreate:
    """Тесты создания велосипедов"""
    bike_data_without_description = {
        "brand": "Stels",
        "model": "Navigator",
        "year": 2019
    }

    async def test_create_bike_success_without_description(self, client: AsyncClient):
        response = await client.post("/bikes", json=self.bike_data_without_description)
        assert response.status_code == 201
        data = response.json()
        assert data["brand"] == "Stels"
        assert data["model"] == "Navigator"
        assert data["year"] == 2019
        assert data["description"] == None
        assert "id" in data

    bike_data_with_description = {
        "brand": "Stels",
        "model": "Navigator",
        "year": 2021,
        "description": "What color is your bugatti?"
    }

    async def test_create_bike_success_with_description(self, client: AsyncClient):
        response = await client.post("/bikes", json=self.bike_data_with_description)
        assert response.status_code == 201
        data = response.json()
        assert data["brand"] == "Stels"
        assert data["model"] == "Navigator"
        assert data["year"] == 2021
        assert data["description"] == "What color is your bugatti?"
        assert "id" in data

    bike_data_invalid_year = {
        "brand": "Stels",
        "model": "Navigator",
        "year": 2000,
    }

    async def test_create_bike_failure_year_less(self, client: AsyncClient):
        response = await client.post("/bikes", json=self.bike_data_invalid_year)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    bike_data_invalid_year_more = {
        "brand": "Stels",
        "model": "Navigator",
        "year": 2030,
    }

    async def test_create_bike_failure_year_more(self, client: AsyncClient):
        response = await client.post("/bikes", json=self.bike_data_invalid_year_more)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
class TestReadBike:
    """Тест GET запросов"""

    async def test_get_bikes_empty(self, client: AsyncClient):
        """Тест получения пустого списка велосипедов"""
        response = await client.get("/bikes")
        assert response.status_code == 200
        assert response.json() == []

    async def fill_db(self, client: AsyncClient):
        bikes_data = [
            {
                "brand": "Stels",
                "model": "Navigator",
                "year": 2022,
                "description": "What color is your bugatti?"
            },
            {
                "brand": "Outleap",
                "model": "Riot Pro",
                "year": 2025,
                "description": "Outleap - русский бренд велосипедов"
            }
        ]
        for bike in bikes_data:
            await client.post("/bikes", json=bike)

    async def test_get_all_bikes(self, client: AsyncClient):
        await self.fill_db(client)
        response = await client.get("/bikes")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_bike_by_id_success(self, client: AsyncClient):
        await self.fill_db(client)
        response = await client.get("/bikes/1")

        assert response.status_code == 200
        data = response.json()
        assert data["brand"] == "Stels"
        assert data["model"] == "Navigator"
        assert data["year"] == 2022
        assert data["description"] == "What color is your bugatti?"

    async def test_get_bike_by_id_failure(self, client: AsyncClient):
        await self.fill_db(client)
        response = await client.get("/bikes/50")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestDeleteBike:
    """Тест DELETE запросов"""
    bike_data = {
        "brand": "Outleap",
        "model": "Riot Pro",
        "year": 2025,
        "description": "Outleap - русский бренд велосипедов"
    }

    async def test_delete_bike_success(self, client: AsyncClient):
        await client.post("/bikes", json=self.bike_data)
        response = await client.delete("/bikes/1")
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    async def test_delete_bike_failure(self, client: AsyncClient):
        await client.post("/bikes", json=self.bike_data)
        response = await client.delete("/bikes/50")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestUpdateBike:
    """Тест PATCH запросов"""

    bike_data = {
        "brand": "No name",
        "model": "Old bike",
        "year": 2021,
    }

    async def test_patch_bike_success(self, client: AsyncClient):
        create_response = await client.post("/bikes", json=self.bike_data)
        bike_id = create_response.json()["id"]

        new_bike_data = {
            "brand": "Stels",
            "model": "Navigator",
        }

        response = await client.patch(f"/bikes/{bike_id}", json=new_bike_data)

        assert response.status_code == 200
        data = response.json()
        assert data["brand"] == "Stels"
        assert data["model"] == "Navigator"
        assert data["year"] == 2021
        assert data["description"] == None

    async def test_patch_bike_success_no_data(self, client: AsyncClient):
        create_response = await client.post("/bikes", json=self.bike_data)
        bike_id = create_response.json()["id"]

        response = await client.patch(f"/bikes/{bike_id}", json={})

        assert response.status_code == 200
        data = response.json()
        assert data["brand"] == "No name"
        assert data["model"] == "Old bike"
        assert data["year"] == 2021

    async def test_patch_bike_failure_no_id(self, client: AsyncClient):
        await client.post("/bikes", json=self.bike_data)

        new_bike_data = {
            "brand": "Stels",
            "model": "Navigator",
        }

        response = await client.patch("/bikes/50", json=new_bike_data)
        assert response.status_code == 404

    async def test_patch_bike_failure_invalid_data(self, client: AsyncClient):
        create_response = await client.post("/bikes", json=self.bike_data)
        bike_id = create_response.json()["id"]

        new_bike_data = {
            "brand": "Stels",
            "model": "Navigator",
            "year": 1900
        }

        response = await client.patch(f"/bikes/{bike_id}", json=new_bike_data)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
class TestBikeRepository:
    """Тестирование репозитория напрямую"""

    async def test_repository_create(self, db_session):
        repository = BikeRepository(db_session)
        bike_data = BikeCreate(brand="Test", model="Model", year=2023)
        bike = await repository.create(bike_data)
        assert bike.id is not None
        assert bike.brand == "Test"

    async def fill_db(self, db_session):
        repository = BikeRepository(db_session)
        bikes_data = [
            BikeCreate(brand="Outleap", model="Riot Pro", year=2025),
            BikeCreate(brand="Corratec", model="Wireguard", year=2021),
        ]
        for bike in bikes_data:
            await repository.create(bike)

    async def test_repository_get_all(self, db_session):
        repository = BikeRepository(db_session)
        await self.fill_db(db_session)
        bikes = await repository.get_all()
        assert len(bikes) == 2

    async def test_repository_get_by_id(self, db_session):
        repository = BikeRepository(db_session)
        await self.fill_db(db_session)
        bike = await repository.get_by_id(1)
        assert bike is not None
        assert bike.id == 1
        assert bike.brand == "Outleap"
        assert bike.model == "Riot Pro"
        assert bike.year == 2025

    async def test_repository_get_by_id_not_found(self, db_session):
        repo = BikeRepository(db_session)
        result = await repo.get_by_id(999)
        assert result is None

    async def test_repository_delete(self, db_session):
        repository = BikeRepository(db_session)
        await self.fill_db(db_session)
        bikes = await repository.get_all()
        assert len(bikes) == 2
        await repository.delete(1)
        bikes = await repository.get_all()
        assert len(bikes) == 1

    async def test_repository_delete_not_found(self, db_session):
        repo = BikeRepository(db_session)
        result = await repo.delete(999)
        assert result is None

    async def test_repository_update(self, db_session):
        repository = BikeRepository(db_session)
        await self.fill_db(db_session)
        bike = await repository.get_by_id(1)
        assert bike.brand == "Outleap"
        assert bike.model == "Riot Pro"
        assert bike.description == None

        new_bike_data = BikeUpdate(
            brand="New Brand",
            model="Millionaire",
            description="New Description"
        )

        new_bike = await repository.patch(bike.id, new_bike_data)
        assert new_bike.brand == "New Brand"
        assert new_bike.model == "Millionaire"
        assert new_bike.description == "New Description"
        assert bike.year == new_bike.year

    async def test_repository_update_not_found(self, db_session):
        repository = BikeRepository(db_session)
        await self.fill_db(db_session)
        new_bike_data = BikeUpdate(
            brand="New Brand",
            model="Millionaire",
            description="New Description"
        )

        new_bike = await repository.patch(500, new_bike_data)
        assert new_bike is None
