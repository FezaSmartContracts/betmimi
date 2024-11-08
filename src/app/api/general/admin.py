from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Query
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_superuser
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_users import crud_users
from ...schemas.users import AdminUpdate, UserRead

router = APIRouter(tags=["administration"])


@router.get("/admins", response_model=PaginatedListResponse[UserRead])
async def read_admins(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int,
) -> dict:
    """
    - Retrieve a paginated list of rate admins.
    - This endpoint allows users to retrieve admins in a paginated format.
    - Args:
        - `request (Request):` The request object.
        - `db (AsyncSession):` The database session.
        - `page (int):` The page number to retrieve.
        - `items_per_page (int):` The number of items per page.
    - Returns:
        - `dict:` A dictionary containing the paginated list of admins.
    """
    admins_data = await crud_users.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=UserRead,
        is_superuser=True
    )
    response: dict[str, Any] = paginated_response(crud_data=admins_data, page=page, items_per_page=items_per_page)
    return response



@router.patch("/update-admin", dependencies=[Depends(get_current_superuser)])
async def update_admin(
    request: Request,
    values: AdminUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    public_address: str = Query(..., description="User Address")
) -> dict[str, str]:
    """
    - Update a specific User(Admin) by Ethereum address.
    - This endpoint allows a superuser to remove or create a super_user.
    - Args:
        - `request (Request):` The request object.
        - `public_address (str):` The address of user to update.
        - `values (AdminUpdate):` The new values for the Admin.
        - `db (AsyncSession):` The database session.
    - Returns:
        - `dict[str, str]:` A success message indicating the update status.
    - Raises:
        - `NotFoundException:` If a user with the specified address is not found.
    """
    address = public_address.lower()
    db_user = await crud_users.get(db=db, public_address=address)
    if db_user is None:
        raise NotFoundException(f"User {address} not found")

    await crud_users.update(
        db,
        AdminUpdate(is_superuser=values.is_admin),
        public_address=address
    )
    return {"message": f"Admin Status for {address} updated to {values.is_admin}"}
