from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, HTTPException
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_predictions import crud_predictions
from ...models.user import PredictionRead

router = APIRouter(tags=["predictions"])



@router.get("/predictions", response_model=PaginatedListResponse[PredictionRead])
async def get_all_predictions(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int
) -> dict:
    """
    - Returns all predictions.
    """
    users_data = await crud_predictions.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        return_as_model=True,
        schema_to_select=PredictionRead,
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response

@router.get("/matchid/predictions", response_model=PaginatedListResponse[PredictionRead])
async def get_predictions_by_matchid(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int
) -> dict:
    """
    - Returns predictions sorted by matchid
    """
    users_data = await crud_predictions.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        return_as_model=True,
        schema_to_select=PredictionRead,
        sort_columns="match_id",
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response

@router.get("/user/latest/predictions", response_model=PaginatedListResponse[PredictionRead])
async def get_all_latest_user_predictions(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int
) -> dict:
    """
    - Returns latest user predictions
    """
    users_data = await crud_predictions.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        return_as_model=True,
        schema_to_select=PredictionRead,
        sort_columns="match_id",
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response