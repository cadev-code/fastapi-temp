from app.models.item import ItemModel


class ItemRepository:
    def __init__(self, db_session: object) -> None:
        # Aquí iría AsyncSession de SQLAlchemy.
        self.db = db_session

    async def get_by_id(self, item_id: int) -> ItemModel | None:
        # Aquí va tu query SQL / ORM
        raise NotImplementedError

    async def create(self, item: ItemModel) -> ItemModel:
        # Aquí va el INSERT / commit
        raise NotImplementedError
