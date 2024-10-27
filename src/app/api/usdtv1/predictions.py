from typing import Annotated, Any, Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel

from fastapi import APIRouter, Depends, Request, HTTPException
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession
from fastcrud import JoinConfig

from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_predictions import crud_predictions
from ...crud.crud_users import crud_users
from ...crud.crud_opponent import crud_opponent
from ...schemas.custom import Date
from ...models.user import (
    Opponent,
    Prediction,
    User
)

from ...schemas.users import (
    UserRead,
    UserBalanceRead,
    UserPublicAddress,
    UserNonce
)
from ...schemas.predictions import (
    PredictionRead,
    PredictionCreate,
    PredictionUpdate,
    PredictionUpdateInternal
)
from ...schemas.opponents import (
    OpponentRead,
    OpponentCreate,
    OpponentUpdate,
    OpponentUpdateInternal
)

router = APIRouter(tags=["predictions"])


@router.post("/dynamic/predictions", response_model=PaginatedListResponse[PredictionRead])
async def get_prediction_dynamically(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int,
    date_info: Optional[Date],
) -> dict:
    """
    Args
    -----
    - `year`: e.g 2024, 
    - `month`: e.g 10 for october,
    - `day`: e.g 18 for 18th

    Returns
    -----
    - All predictions(Both active and non-active) with a `filter`:
    - All predictions with ``created_at` greater than specified timestamp.
    """
    users_data = await crud_predictions.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        return_as_model=True,
        schema_to_select=PredictionRead,
        created_at__gt=datetime(date_info.year, date_info.month, date_info.day, tzinfo=timezone.utc),
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response

@router.get("/latest/predictions", response_model=PaginatedListResponse[PredictionRead])
async def get_latest_predictions(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    year: int,
    month: int,
    day: int,
    page: int,
    items_per_page: int
) -> dict:
    """
    Args
    -----
    - `year`: e.g 2024, 
    - `month`: e.g 10 for october,
    - `day`: e.g 18 for 18th

    Returns
    -----
    - All predictions(Both active and non-active) with a `filter`:
    - All predictions with ``created_at` greater than specified timestamp.
    """
    users_data = await crud_predictions.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        return_as_model=True,
        schema_to_select=PredictionRead,
        created_at__gt=datetime(year, month, day, tzinfo=timezone.utc),
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response

@router.get("/matchid/predictions", response_model=PaginatedListResponse[PredictionRead])
async def get_unsettled_predictions_by_matchid(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int
) -> dict:
    """
    Returns
    -----
    - Returns predictions sorted by column `match_id` and filter `settled=False`
    """
    users_data = await crud_predictions.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        return_as_model=True,
        schema_to_select=PredictionRead,
        sort_columns="match_id",
        settled=False,
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response

@router.get("/me/active/predictions", response_model=PaginatedListResponse[PredictionRead])
async def get_all_latest_user_predictions(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int
) -> dict:
    """
    - Returns active(`settled=False`) user predictions
    """
    users_data = await crud_users.get_multi_joined(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=PredictionRead,
        joins_config=[
        JoinConfig(
            model=Opponent,
            join_on=(Prediction.id == Opponent.prediction_id),
            schema_to_select=OpponentRead,
            join_type="left",
        )
        ],
        settled=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response

@router.get("/all/active/predictions", response_model=PaginatedListResponse[OpponentRead])
async def get_all_latest_user_predictions(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int
) -> dict:
    """
    - Returns active(`settled=False`) user predictions
    """
    users_data = await crud_opponent.get_multi_joined(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        join_on=(Opponent.prediction_id == Prediction.id),
        schema_to_select=OpponentRead,
        join_model=Prediction,
        return_as_model=True,
        join_schema_to_select=PredictionRead,
        #settled=False,
        relationship_type='one-to-many',
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response


#-----------------------------Get predictions---------------------------------#
@router.get("/active/predictions", response_model=PaginatedListResponse[PredictionRead])
async def get_all_latest_user_predictions(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int
) -> dict:
    """
    - Returns a paginated list of active(`settled=False`) predictions
    """
    users_data = await crud_predictions.get_multi_joined(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        join_on=(Prediction.user_id == User.id),
        schema_to_select=PredictionRead,
        join_model=User,
        return_as_model=True,
        join_schema_to_select=PredictionRead,
        join_type="left",
        settled=False,
        relationship_type='one-to-many',
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response



#------------------------------Create prediction------------------------------------#
@router.post("/auth", response_model=PredictionCreate)
async def prediction_create(
    request: Request,
    user_address: UserPublicAddress,
    prediction_data: PredictionCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict:
    public_address = str(user_address.public_address).lower()
    
    wallet: UserRead | None = await crud_users.get(
        db=db, schema_to_select=UserRead, public_address=public_address
    )
    if wallet is None:
        raise HTTPException(status_code=404, detail=f"User {public_address} not found")

    new_user_prediction: PredictionCreate = await crud_predictions.create(
        db,
        PredictionCreate(
        user_id=wallet["id"],  # Link prediction to the found/created user
        index=prediction_data.index,  # Assuming index is part of PredictionCreate.
        layer=prediction_data.layer.lower(),
        match_id=prediction_data.match_id,
        result=prediction_data.result,
        amount=prediction_data.amount,
        settled=prediction_data.settled,
        total_opponent_wager=prediction_data.total_opponent_wager,
        f_matched=prediction_data.f_matched,
        p_matched=prediction_data.p_matched,
        for_sale=prediction_data.for_sale,
        sold=prediction_data.sold,
        price=prediction_data.price
        )
    )
    return new_user_prediction


##########--create Opponent-----######
@router.post("/opp", response_model=OpponentCreate)
async def create_opponent(
    request: Request,
    index: int,
    opponent_data: OpponentCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict:
    #public_address = str(user_address.public_address).lower()
    
    wallet: OpponentRead | None = await crud_predictions.get(
        db=db, schema_to_select=OpponentRead, id=index
    )
    if wallet is None:
        raise HTTPException(status_code=404, detail=f"User {index} not found")

    new_user_prediction: OpponentCreate = await crud_opponent.create(
        db,
        OpponentCreate(
        prediction_id=index,  # Link prediction to the found/created user
        opponent_address=opponent_data.opponent_address.lower(),
        opponent_wager=opponent_data.opponent_wager,  # Assuming index is part of PredictionCreate
        result=opponent_data.result
        )
    )
    return new_user_prediction
