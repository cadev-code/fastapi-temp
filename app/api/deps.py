from typing import Annotated

from fastapi import Depends

from app.repositories.item_repository import ItemRepository
from app.services.item_service import ItemService


def get_db_session() -> object:
    # Yield de la sesión asíncrona de BD
    return object()


def get_item_repository(
    db: Annotated[object, Depends(get_db_session)],
) -> ItemRepository:
    return ItemRepository(db)


def get_item_service(
    repo: Annotated[ItemRepository, Depends(get_item_repository)],
) -> ItemService:
    return ItemService(repo)
