from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...crud.crud_matches import crud_matches
from ...schemas.games import GameRead

router = APIRouter(tags=["games"])

@router.get("/registered-games", response_model=PaginatedListResponse[GameRead])
async def get_all_registered_games(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int
) -> dict:
    """
    - Returns a paginated list of all registered games that are not yet resolved
    """
    user_data = await crud_matches.get_multi(
        db,
        schema_to_select=GameRead,
        nest_joins=True,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        resolved=False
    )
    response: dict[str, Any] = paginated_response(
        crud_data=user_data,
        page=page,
        items_per_page=items_per_page
    )
    return response