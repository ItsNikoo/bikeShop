import pytest
from httpx import AsyncClient

from repositories.brand_repository import BrandRepository
from schemas import BrandCreate, BrandUpdate


@pytest.mark.asyncio
class TestBrandCreate:
    """Тесты POST-запросов брендов"""
    brand_data = {
        "name": "Brand",
        "description": "description bro",
        "country": "Russia",
    }

    invalid_data = {
        "name": "Brand",
    }

    async def test_create_brand_success(self, client: AsyncClient):
        response = await client.post("/brands", json=self.brand_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Brand"
        assert data["description"] == "description bro"
        assert data["country"] == "Russia"
        assert "id" in data

    async def test_create_brand_failure(self, client: AsyncClient):
        response = await client.post("/brands", json=self.invalid_data)
        assert response.status_code == 422
        assert response.status_code != 201


@pytest.mark.asyncio
class TestBrandRead:
    """Тесты GET-запросов брендов"""

    async def test_get_brands_empty(self, client: AsyncClient):
        response = await client.get("/brands")
        assert response.status_code == 200
        assert response.json() == []

    @staticmethod
    async def fill_db(client: AsyncClient):
        brand_data = [
            {
                "name": "Brand1",
                "description": "description bro 1",
                "country": "Russia",
            },
            {
                "name": "Brand2",
                "description": "description bro 2",
                "country": "Russia",
            }
        ]
        for brand in brand_data:
            await client.post("/brands", json=brand)

    async def test_get_brands(self, client: AsyncClient):
        await self.fill_db(client)
        response = await client.get("/brands")
        data = response.json()
        assert response.status_code == 200
        assert len(data) == 2
        assert data[0]["name"] == "Brand1"
        assert data[0]["description"] == "description bro 1"
        assert data[0]["country"] == "Russia"

    async def test_get_brand_by_id(self, client: AsyncClient):
        await self.fill_db(client)
        response = await client.get("/brands/2")
        data = response.json()
        assert response.status_code == 200
        assert data["name"] == "Brand2"
        assert data["description"] == "description bro 2"
        assert data["country"] == "Russia"


@pytest.mark.asyncio
class TestBrandUpdate:
    """Тесты PATCH-запросов брендов"""
    brand_data = {
        "name": "Brand",
        "description": "description",
        "country": "Sweden",
    }

    async def test_patch_brand_success(self, client: AsyncClient):
        create_response = await client.post("/brands", json=self.brand_data)
        brand_id = create_response.json()["id"]

        new_brand_data = {
            "name": "Corratec",
            "description": "Новое описание",
        }

        response = await client.patch(f"/brands/{brand_id}", json=new_brand_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Corratec"
        assert data["description"] == "Новое описание"
        assert data["country"] == "Sweden"

    async def test_patch_brand_failure(self, client: AsyncClient):
        create_response = await client.post("/brands", json=self.brand_data)

        new_brand_data = {
            "name": "Corratec",
            "description": "Новое описание",
        }

        response = await client.patch(f"/brands/500", json=new_brand_data)

        assert response.status_code == 404


@pytest.mark.asyncio
class TestBrandDelete:
    """Тесты DELETE-запросов брендов"""
    brand_data = {
        "name": "Corratec",
        "description": "description",
        "country": "Russia",
    }

    async def fill_db(self, client: AsyncClient): await client.post("/brands", json=self.brand_data)

    async def test_brand_delete_success(self, client: AsyncClient):
        await self.fill_db(client)
        response = await client.delete("/brands/1")
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    async def test_brand_delete_failure(self, client: AsyncClient):
        await self.fill_db(client)
        response = await client.delete("/brands/100")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestBrandRepository:
    """Тестирование репозитория брендов напрямую"""

    async def test_repository_create(self, db_session):
        repository = BrandRepository(db_session)
        brand_data = BrandCreate(name="Stels", description="desc",
                                 country="Russia")  # предполагаем, что в BrandCreate поле называется name
        brand = await repository.create(brand_data)

        assert brand.id is not None
        assert brand.name == "Stels"
        assert brand.description == "desc"
        assert brand.country == "Russia"

    @staticmethod
    async def fill_db(db_session):
        repository = BrandRepository(db_session)
        brands_data = [
            BrandCreate(name="Stels", description="desc", country="Russia"),
            BrandCreate(name="Outleap", description="desc", country="Russia"),
            BrandCreate(name="Corratec", description="desc", country="Germany"),
        ]
        for brand in brands_data:
            await repository.create(brand)

    async def test_repository_get_all(self, db_session):
        repository = BrandRepository(db_session)
        await self.fill_db(db_session)

        brands = await repository.get_all()
        assert len(brands) == 3

        # Проверяем, что названия правильные (порядок не гарантирован, но можно проверить множество)
        names = {b.name for b in brands}
        assert names == {"Stels", "Outleap", "Corratec"}
        countries = {b.country for b in brands}
        assert countries == {"Russia", "Russia", "Germany"}

    async def test_repository_get_by_id(self, db_session):
        repository = BrandRepository(db_session)
        await self.fill_db(db_session)

        brand = await repository.get_by_id(1)
        assert brand is not None
        assert brand.id == 1
        assert brand.name == "Stels"  # первый созданный — Stels

    async def test_repository_get_by_id_not_found(self, db_session):
        repo = BrandRepository(db_session)
        result = await repo.get_by_id(999)
        assert result is None

    async def test_repository_delete_success(self, db_session):
        repository = BrandRepository(db_session)
        await self.fill_db(db_session)

        brands_before = await repository.get_all()
        assert len(brands_before) == 3

        result = await repository.delete(2)  # удаляем Outleap (id=2)
        assert result == {"status": "success"}

        brands_after = await repository.get_all()
        assert len(brands_after) == 2
        names = {b.name for b in brands_after}
        assert "Outleap" not in names

    async def test_repository_delete_not_found(self, db_session):
        repo = BrandRepository(db_session)
        await self.fill_db(db_session)

        result = await repo.delete(999)
        assert result is None

        # Убеждаемся, что данные не пострадали
        brands = await repo.get_all()
        assert len(brands) == 3

    async def test_repository_patch_success(self, db_session):
        repository = BrandRepository(db_session)
        await self.fill_db(db_session)

        brand = await repository.get_by_id(1)
        assert brand.name == "Stels"

        update_data = BrandUpdate(
            name="STELS Premium",
            description="Самые лучшие велосипеды",
            country="China"
        )

        updated_brand = await repository.patch(1, update_data)

        assert updated_brand is not None
        assert updated_brand.id == 1
        assert updated_brand.name == "STELS Premium"
        assert updated_brand.description == "Самые лучшие велосипеды"
        assert updated_brand.country == "China"

    async def test_repository_patch_partial_update(self, db_session):
        repository = BrandRepository(db_session)

        full_data = BrandCreate(name="Merida", description="Велосипеды Merida", country="Taiwan")
        created_brand = await repository.create(full_data)

        assert created_brand.id is not None
        assert created_brand.name == "Merida"
        assert created_brand.country == "Taiwan"

        partial_update = BrandUpdate(name="MERIDA")

        updated = await repository.patch(created_brand.id, partial_update)

        assert updated is not None
        assert updated.id == created_brand.id
        assert updated.name == "MERIDA"
        assert updated.description == "Велосипеды Merida"
        assert updated.country == "Taiwan"

    async def test_repository_patch_not_found(self, db_session):
        repository = BrandRepository(db_session)
        await self.fill_db(db_session)

        update_data = BrandUpdate(name="Ghost Brand")

        result = await repository.patch(500, update_data)
        assert result is None

        # База не изменилась
        brands = await repository.get_all()
        assert len(brands) == 3
