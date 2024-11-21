import asyncio
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_superuser
from app.core.db.database import async_get_db
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.web3_services.arbitrum_one.websocket_service import WebSocketMonitor
from app.crud.crud_users import crud_users
from app.schemas.users import AdminUpdate, UserRead
from app.core.web3_services.get_functions.usdt.functions import (
    get_count_for_usdt_contracts,
    game_info,
    is_admin,
    is_whitelisted,
    fee_percentage,
    future_owner,
    current_owner
)

router = APIRouter(tags=["administration"])


websocket_task = None

@router.post(
    "/start-websocket",
    #dependencies=[
    #    Depends(get_admin),
    #    Depends(rate_limiter)
    #]
)
async def start_websocket():
    """Should `Strictly` be called `only` when necessary"""
    global websocket_task

    if websocket_task and not websocket_task.done():
        raise HTTPException(status_code=400, detail="WebSocket monitor is already running.")
    
    monitor = WebSocketMonitor()
    websocket_task = asyncio.create_task(monitor.start())

    return {"status": "WebSocket monitor started"}


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


@router.get("/counter")
async def read_number(
    request: Request,
    game_id: int = Query(..., description="Match ID")
):
    """
    - Returns the current number of predictions for a given match from each contract
    """
    counter = await get_count_for_usdt_contracts(game_id)
    return counter

@router.get("/owner")
async def get_current_owner(
    request: Request,
    data_key_name: str = Query(..., description="Key for contract data in the `deployments.json` file")
) -> dict:
    """
    - Returns the current owner for a given contract
    """
    owner = {}
    owner['data'] = await current_owner(data_key_name)
    return owner

@router.get("/pending-owner")
async def get_future_owner(
    request: Request,
    data_key_name: str = Query(..., description="Key for contract data in the `deployments.json` file")
) -> dict:
    """
    - Returns the pending owner for a given contract
    """
    owner = {}
    owner['data'] = await future_owner(data_key_name)
    return owner

@router.get("/fee-percentage")
async def get_fee_percentage(
    request: Request,
    data_key_name: str = Query(..., description="Key for contract data in the `deployments.json` file")
) -> dict:
    """
    - Returns the current fee percentage for a given contract.
    """
    owner = {}
    owner['data'] = await fee_percentage(data_key_name)
    return owner

@router.get("/game-info")
async def get_fee_percentage(
    request: Request,
    match_id: int = Query(..., description="Match ID")
) -> dict:
    """
    - Returns current data about a given match. It should be already registered on-chain
    """
    game = {}
    game['data'] = await game_info(match_id)
    return game

@router.get("/is-admin")
async def is_admin_address(
    request: Request,
    address: str = Query(..., description="Contract or EOA address"),
    data_key_name: str = Query(..., description="Key for contract data in the `deployments.json` file")
) -> dict:
    """
    - Returns a boolean value for the admin status of a given address.
    """
    value = {}
    value['data'] = await is_admin(address, data_key_name)
    return value

@router.get("/is-whitelisted")
async def is_whitelisted_address(
    request: Request,
    address: str = Query(..., description="Contract or EOA address"),
    data_key_name: str = Query(..., description="Key for contract data in the `deployments.json` file")
) -> dict:
    """
    - Returns a boolean value for if an address is whitelisted or not.
    """
    value = {}
    value['data'] = await is_whitelisted(address, data_key_name)
    return value