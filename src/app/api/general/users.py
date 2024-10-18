from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_rate_limit import crud_rate_limits
from ...crud.crud_users import crud_users
from ...schemas.users import UserRead, UserEmailUpdate

router = APIRouter(tags=["users"])




@router.get("/users", response_model=PaginatedListResponse[UserRead])
async def read_users(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], page: int, items_per_page: int
) -> dict:
    users_data = await crud_users.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        return_as_model=True,
        schema_to_select=UserRead,
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/user/me/", response_model=UserRead)
async def read_users_me(request: Request, current_user: Annotated[UserRead, Depends(get_current_user)]) -> UserRead:
    return current_user


@router.get("/user/{public_address}", response_model=UserRead)
async def read_user(request: Request, public_address: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict:
    db_user: UserRead | None = await crud_users.get(
        db=db, schema_to_select=UserRead, public_address=public_address.lower(), is_deleted=False
    )
    if db_user is None:
        raise NotFoundException("User not found")

    return db_user

@router.patch("/user/email/")
async def patch_user_email(
    request: Request,
    values: UserEmailUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    """
    Add or update the user's email.
    - If the email is not set, this endpoint will add it.
    - If the email is set, this endpoint will update it.
    Args:
        request (Request): The request object.
        values (UserEmailUpdate): The new email data.
        current_user (UserRead): The authenticated user's current data.
        db (AsyncSession): The database session.
    Returns:
        dict[str, str]: A success message.
    Raises:
        NotFoundException: If the user is not found.
        ForbiddenException: If the user is not authorized to update another user's email.
        DuplicateValueException: If the email is already taken.
    """

    db_user = await crud_users.get(db=db, schema_to_select=UserRead, id=current_user.id)
    if not db_user:
        raise NotFoundException("User not found")

    if values.email != db_user["email"]:
        existing_email_user = await crud_users.exists(db=db, email=values.email)
        if existing_email_user:
            raise DuplicateValueException("Email is already registered")

    update_data = {"email": values.email}
    await crud_users.update(db=db, object=update_data, id=current_user.id)
    return {"message": "Email updated successfully"}



@router.get("/user/{public_address}/rate_limits", dependencies=[Depends(get_current_superuser)])
async def read_user_rate_limits(
    request: Request, public_address: str, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any]:
    """
    Retrieve rate limits associated with a user by public address.
    Args:
        request (Request): The request object.
        public_address (str): The public address of the user.
        db (AsyncSession): The database session.
    Returns:
        dict[str, Any]: The user's rate limits.
    Raises:
        NotFoundException: If the user is not found.
    """
    # Retrieve the user based on the public address
    db_user = await crud_users.get(db=db, public_address=public_address, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User not found")

    # Retrieve rate limits associated with the user directly
    user_rate_limits = await crud_rate_limits.get_multi(db=db, user_id=db_user["id"])

    return {
        "user_id": db_user["id"],
        "public_address": db_user["public_address"],
        "rate_limits": user_rate_limits["data"],
    }

