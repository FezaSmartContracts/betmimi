from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_superuser
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException, RateLimitException
from ...crud.crud_rate_limit import crud_rate_limits
from ...models.rate_limit import RateLimitCreate, RateLimitRead, RateLimitUpdate

router = APIRouter(tags=["rate_limits"])

@router.post("/rate_limit", dependencies=[Depends(get_current_superuser)], status_code=201)
async def create_rate_limit(
    request: Request, rate_limit: RateLimitCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> RateLimitRead:
    """
    - Create a new rate limit.
    - This endpoint allows a superuser to create a new rate limit rule with a specified path, limit, and period.
    - Args:
        - `request (Request):` The request object.
        - `rate_limit (RateLimitCreate):` The rate limit information to create.
        - `db (AsyncSession):` The database session.
    - Returns:
        - `RateLimitRead:` The created rate limit details.
    - Raises:
        - `DuplicateValueException:` If a rate limit with the same name already exists.
    """
    #rate_limit_internal_dict = rate_limit.model_dump()
    db_rate_limit = await crud_rate_limits.exists(db=db, name=rate_limit.name)
    if db_rate_limit:
        raise DuplicateValueException("Rate Limit Name not available")

    created_rate_limit: RateLimitRead = await crud_rate_limits.create(
        db,
        RateLimitCreate(name=rate_limit.name)
    )
    return created_rate_limit

@router.get("/rate_limits", response_model=PaginatedListResponse[RateLimitRead])
async def read_rate_limits(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10,
) -> dict:
    """
    - Retrieve a paginated list of rate limits.
    - This endpoint allows users to retrieve rate limits in a paginated format.
    - Args:
        - `request (Request):` The request object.
        - `db (AsyncSession):` The database session.
        - `page (int):` The page number to retrieve.
        - `items_per_page (int):` The number of items per page.
    - Returns:
        - `dict:` A dictionary containing the paginated list of rate limits.
    """
    rate_limits_data = await crud_rate_limits.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=RateLimitRead
    )
    response: dict[str, Any] = paginated_response(crud_data=rate_limits_data, page=page, items_per_page=items_per_page)
    return response

@router.get("/rate_limit/{id}", response_model=RateLimitRead)
async def read_rate_limit(
    request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict:
    """
    - Retrieve a specific rate limit by ID.
    - This endpoint allows users to retrieve the details of a specific rate limit by its ID.
    - Args:
        - `request (Request):` The request object.
        - `id (int):` The ID of the rate limit to retrieve.
        - `db (AsyncSession):` The database session.
    - Returns:
        - `dict:` The details of the rate limit.
    - Raises:
        - `NotFoundException:` If the rate limit with the specified ID is not found.
    """
    db_rate_limit: dict | None = await crud_rate_limits.get(db=db, schema_to_select=RateLimitRead, id=id)
    if db_rate_limit is None:
        raise NotFoundException("Rate Limit not found")

    return db_rate_limit

@router.patch("/rate_limit/{id}", dependencies=[Depends(get_current_superuser)])
async def update_rate_limit(
    request: Request,
    id: int,
    values: RateLimitUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    """
    - Update a specific rate limit by ID.
    - This endpoint allows a superuser to update an existing rate limit's path, limit, period, or name.
    - Args:
        - `request (Request):` The request object.
        - `id (int):` The ID of the rate limit to update.
        - `values (RateLimitUpdate):` The new values for the rate limit.
        - `db (AsyncSession):` The database session.
    - Returns:
        - `dict[str, str]:` A success message indicating the update status.
    - Raises:
        - `NotFoundException:` If the rate limit with the specified ID is not found.
    """
    db_rate_limit = await crud_rate_limits.get(db=db, schema_to_select=RateLimitRead, id=id)
    if db_rate_limit is None:
        raise NotFoundException("Rate Limit not found")

    await crud_rate_limits.update(
        db=db,
        allow_multiple=True,
        object=values, id=db_rate_limit["id"]
    )
    return {"message": "Rate Limit updated"}

@router.delete("/rate_limit/{id}", dependencies=[Depends(get_current_superuser)])
async def delete_rate_limit(
    request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    """
    - Delete a specific rate limit by ID.
    - This endpoint allows a superuser to delete an existing rate limit by its ID.
    - Args:
        - `request (Request):` The request object.
        - `id (int):` The ID of the rate limit to delete.
        - `db (AsyncSession):` The database session.
    - Returns:
        - `dict[str, str]:` A success message indicating the deletion status.
    - Raises:
        - `NotFoundException:` If the rate limit with the specified ID is not found.
    """
    db_rate_limit = await crud_rate_limits.get(db=db, schema_to_select=RateLimitRead, id=id)
    if db_rate_limit is None:
        raise NotFoundException("Rate Limit not found")

    await crud_rate_limits.delete(db=db, id=db_rate_limit["id"])
    return {"message": "Rate Limit deleted"}
