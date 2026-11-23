from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.item import ItemModel
from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemCreate


class ItemService:
    def __init__(self, repository: ItemRepository) -> None:
        self.repository = repository

    async def get_item(self, item_id: int) -> ItemModel:
        item = await self.repository.get_by_id(item_id)
        if not item:
            raise NotFoundError(f"Item with id {item_id} not found")
        return item

    async def create_item(self, data: ItemCreate) -> ItemModel:
        if data.price <= 0:
            raise BusinessRuleError("El precio debe ser mayor que cero")

        new_item = ItemModel(name=data.name, price=data.price)
        return await self.repository.create(new_item)
