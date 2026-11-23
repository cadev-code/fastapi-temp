from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import get_item_service
from app.schemas.item import ItemCreate, ItemResponse
from app.services.item_service import ItemService

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: ItemCreate,
    service: Annotated[ItemService, Depends(get_item_service)],
) -> ItemResponse:
    item = await service.create_item(payload)
    return ItemResponse.model_validate(item)
