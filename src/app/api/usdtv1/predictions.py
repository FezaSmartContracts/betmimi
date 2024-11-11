from typing import Annotated, Any, Optional, Dict
from datetime import datetime, timezone
from sqlmodel import SQLModel

from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession
from fastcrud import JoinConfig

from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_predictions import crud_predictions
from ...crud.crud_users import crud_users
from ...models.user import Opponent, Prediction, User

from ...schemas.users import UserRead, QuickAdminRead
from ...schemas.predictions import PredictionRead, PredictionAndOpponents
from ...schemas.opponents import OpponentRead
from ...schemas.custom import Count
from app.core.logger import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["predictions"])


@router.get("/count-all", response_model=Count)
async def get_all_active_predictions_count(
    db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict:
    """
    - Returns the total number of all activae lays
    """
    preds_count = await crud_predictions.count(
        db,
        settled=False
    )
    return Count(number=preds_count)

    
@router.get("/count-by-matchid", response_model=Count)
async def get_predictions_for_matchid(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    matchid: int = Query(..., description="The ID of the match")
) -> dict:
    """
    - Returns the number of lays for a given match
    """
    preds = await crud_predictions.count(
        db,
        match_id=matchid
    )
    return Count(number=preds)

@router.get("/count-user-active-preds", response_model=Count)
async def get_predictions_for_matchid(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    public_address: str = Query(..., description="User Address")
) -> dict:
    """
    - Returns the number of active lays for a given user
    """
    public_address = public_address.lower()
    preds = await crud_predictions.count(
        db,
        public_address=public_address
    )
    return Count(number=preds)

@router.get("/prediction")
async def get_prediction(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    pred_id: int = Query(..., description="The ID of the prediction")
) -> dict:
    """
    - Returns a prediction plus associated opponents if any
    """
    pred_data = await crud_predictions.get_joined(
        db,
        schema_to_select=PredictionRead,
        join_model=Opponent,
        join_schema_to_select=OpponentRead,
        relationship_type="one-to-many",
        nest_joins=True,
        id=pred_id
    )
    if pred_data:
        return pred_data
    else:
        return {}

@router.get("/user-specific-history", dependencies=[Depends(get_current_superuser)])
async def get_all_user_specific_prediction_history(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    user_address: str = Query(..., description="User's Public Address")
) -> dict:
    """
    - Returns a user-specific predictions history.
    - This endpoint is primarily intended to cover a scenerio(where in this case other methods shall only consider the buyer) 
    when a user sells their pred.
    """
    public_address = user_address.lower()
    user_data = await crud_users.get_joined(
        db,
        schema_to_select=UserRead,
        nest_joins=True,
        joins_config=[
            JoinConfig(
                model=Prediction,
                join_on=User.id == Prediction.user_id,
                schema_to_select=PredictionRead,
                relationship_type="one-to-many"
            )
        ],
        public_address=public_address
    )
    if user_data:
        return user_data
    else:
        return {}
    
@router.get(
    "/paginated-history",
    dependencies=[Depends(get_current_superuser)],
    response_model=PaginatedListResponse[PredictionRead]
)
async def get_all_user_prediction_history(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int,
    user_address: str = Query(..., description="User's Public Address"),
) -> dict:
    """
    - Returns a paginated list of all user's predictions
    """
    public_address = user_address.lower()
    user_data = await crud_predictions.get_multi(
        db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=PredictionRead,
        nest_joins=True,
        layer=public_address
    )
    response: dict[str, Any] = paginated_response(
        crud_data=user_data,
        page=page,
        items_per_page=items_per_page
    )
    return response

@router.get(
    "/user-active-predictions",
    dependencies=[Depends(get_current_superuser)],
    response_model=PaginatedListResponse[PredictionRead]
)
async def get_all_user_active_predictions(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int,
    user_address: str = Query(..., description="User's Public Address")
) -> dict:
    """
    - Returns all user's active lays(unsettled) without backs
    """
    public_address = user_address.lower()
    user_data = await crud_predictions.get_multi(
        db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=PredictionRead,
        layer=public_address,
        settled=False
    )
    response: dict[str, Any] = paginated_response(
        crud_data=user_data,
        page=page,
        items_per_page=items_per_page
    )
    return response


@router.get("/active-predictions-and-opponents", response_model=PaginatedListResponse[dict])
async def get_all_active_prediction_and_opponents(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int
) -> dict:
    """
    - Returns a paginated list of all users' lays alongside backs
    """
    user_data = await crud_predictions.get_multi_joined(
        db,
        schema_to_select=PredictionRead,
        nest_joins=True,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        joins_config=[
            JoinConfig(
                model=Opponent,
                join_on=Prediction.id == Opponent.prediction_id,
                schema_to_select=OpponentRead,
                relationship_type="one-to-many"
            )
        ],
        settled=False
    )
    response: dict[str, Any] = paginated_response(
        crud_data=user_data,
        page=page,
        items_per_page=items_per_page
    )
    return response

@router.get("/active-preds-and-opps_by-matchid", response_model=PaginatedListResponse[dict])
async def get_all_active_prediction_and_opponents_by_matchid(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int,
    matchid: int = Query(..., description="Match Id")
) -> dict:
    """
    - Returns a paginated list of all users' predictions filtered by matchid
    """
    user_data = await crud_predictions.get_multi_joined(
        db,
        schema_to_select=PredictionRead,
        nest_joins=True,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        joins_config=[
            JoinConfig(
                model=Opponent,
                join_on=Prediction.id == Opponent.prediction_id,
                schema_to_select=OpponentRead,
                relationship_type="one-to-many"
            )
        ],
        match_id=matchid,
        settled=False
    )
    response: dict[str, Any] = paginated_response(
        crud_data=user_data,
        page=page,
        items_per_page=items_per_page
    )
    return response

@router.get("/active-preds-sort-by-id-and-amount", response_model=PaginatedListResponse[dict])
async def get_all_active_predictions_sorted_by_id_and_amount(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int,
    matchid: int = Query(..., description="Match Id")
) -> dict:
    """
    - Returns a paginated list of all users' active predictions filtered by matchid and sorted by amount
    """
    user_data = await crud_predictions.get_multi_joined(
        db,
        schema_to_select=PredictionRead,
        nest_joins=True,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        joins_config=[
            JoinConfig(
                model=Opponent,
                join_on=Prediction.id == Opponent.prediction_id,
                schema_to_select=OpponentRead,
                relationship_type="one-to-many"
            )
        ],
        match_id=matchid,
        settled=False,
        sort_columns=['amount'],
        sort_orders=['desc']
    )
    response: dict[str, Any] = paginated_response(
        crud_data=user_data,
        page=page,
        items_per_page=items_per_page
    )
    return response

@router.get("/active-preds-sort-by-id-and-time-0", response_model=PaginatedListResponse[dict])
async def get_all_active_predictions_sorted_by_id_and_time_0(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int,
    matchid: int = Query(..., description="Match Id")
) -> dict:
    """
    - Returns a paginated list of all users' active predictions filtered by matchid and sorted by 
    `created_at` timestamp in ascending order
    """
    user_data = await crud_predictions.get_multi_joined(
        db,
        schema_to_select=PredictionRead,
        nest_joins=True,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        joins_config=[
            JoinConfig(
                model=Opponent,
                join_on=Prediction.id == Opponent.prediction_id,
                schema_to_select=OpponentRead,
                relationship_type="one-to-many"
            )
        ],
        match_id=matchid,
        settled=False,
        sort_columns=['created_at'],
        sort_orders=['asc']
    )
    response: dict[str, Any] = paginated_response(
        crud_data=user_data,
        page=page,
        items_per_page=items_per_page
    )
    return response

@router.get("/active-preds-sort-by-id-and-time-1", response_model=PaginatedListResponse[dict])
async def get_all_active_predictions_sorted_by_id_and_time_1(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int,
    matchid: int = Query(..., description="Match Id")
) -> dict:
    """
    - Returns a paginated list of all users' active predictions filtered by matchid and sorted by 
    `created_at` timestamp in descending order
    """
    user_data = await crud_predictions.get_multi_joined(
        db,
        schema_to_select=PredictionRead,
        nest_joins=True,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        joins_config=[
            JoinConfig(
                model=Opponent,
                join_on=Prediction.id == Opponent.prediction_id,
                schema_to_select=OpponentRead,
                relationship_type="one-to-many"
            )
        ],
        match_id=matchid,
        settled=False,
        sort_columns=['created_at'],
        sort_orders=['desc'],
    )
    response: dict[str, Any] = paginated_response(
        crud_data=user_data,
        page=page,
        items_per_page=items_per_page
    )
    return response

@router.get("/active-preds-sort-by-id-and-full-matching", response_model=PaginatedListResponse[dict])
async def get_all_active_predictions_sorted_by_id_and_full_matching(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int,
    matchid: int = Query(..., description="Match Id")
) -> dict:
    """
    - Returns a paginated list of all users' predictions filtered by matchid 
    and sorted by whether they are fully matched
    """
    user_data = await crud_predictions.get_multi_joined(
        db,
        schema_to_select=PredictionRead,
        nest_joins=True,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        joins_config=[
            JoinConfig(
                model=Opponent,
                join_on=Prediction.id == Opponent.prediction_id,
                schema_to_select=OpponentRead,
                relationship_type="one-to-many"
            )
        ],
        match_id=matchid,
        settled=False,
        f_matched=True
    )
    response: dict[str, Any] = paginated_response(
        crud_data=user_data,
        page=page,
        items_per_page=items_per_page
    )
    return response

@router.get("/active-preds-sort-by-id-and-partial-matching", response_model=PaginatedListResponse[dict])
async def get_all_active_predictions_sorted_by_id_and_partial_matching(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int,
    matchid: int = Query(..., description="Match Id")
) -> dict:
    """
    - Returns a paginated list of all users' predictions filtered by matchid 
    and sorted by whether they are partially matched
    """
    user_data = await crud_predictions.get_multi_joined(
        db,
        schema_to_select=PredictionRead,
        nest_joins=True,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        joins_config=[
            JoinConfig(
                model=Opponent,
                join_on=Prediction.id == Opponent.prediction_id,
                schema_to_select=OpponentRead,
                relationship_type="one-to-many"
            )
        ],
        match_id=matchid,
        settled=False,
        f_matched=False,
        p_matched=True
    )
    response: dict[str, Any] = paginated_response(
        crud_data=user_data,
        page=page,
        items_per_page=items_per_page
    )
    return response

@router.get("/active-preds-sort-by-id-and-unmatched", response_model=PaginatedListResponse[dict])
async def get_all_active_predictions_sorted_by_id_and_unmatched(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int,
    matchid: int = Query(..., description="Match Id")
) -> dict:
    """
    - Returns a paginated list of all users' predictions filtered by matchid 
    and sorted by whether they are un-matched
    """
    user_data = await crud_predictions.get_multi_joined(
        db,
        schema_to_select=PredictionRead,
        nest_joins=True,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        joins_config=[
            JoinConfig(
                model=Opponent,
                join_on=Prediction.id == Opponent.prediction_id,
                schema_to_select=OpponentRead,
                relationship_type="one-to-many"
            )
        ],
        match_id=matchid,
        settled=False,
        f_matched=False,
        p_matched=False
    )
    response: dict[str, Any] = paginated_response(
        crud_data=user_data,
        page=page,
        items_per_page=items_per_page
    )
    return response

#----------------Backs----------------------------------------------------
@router.get(
    "/user-backs-history",
    dependencies=[Depends(get_current_superuser)],
    response_model=PaginatedListResponse[dict]
)
async def get_all_user_backing_histroy(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int,
    user_address: str = Query(..., description="User's Public Address")
) -> dict:
    """
    - Returns all user's backing history
    """
    public_address = user_address.lower()
    user_data = await crud_predictions.get_multi_joined(
        db,
        schema_to_select=PredictionAndOpponents,
        nest_joins=True,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        joins_config=[
            JoinConfig(
                model=Opponent,
                join_on=Prediction.id == Opponent.prediction_id,
                schema_to_select=OpponentRead,
                relationship_type="one-to-many",
                filters={
                    "opponent_address": public_address
                }
            )
        ]
    )
    response: dict[str, Any] = paginated_response(
        crud_data=user_data,
        page=page,
        items_per_page=items_per_page
    )
    return response

@router.get(
    "/user-active-backs-history",
    dependencies=[Depends(get_current_superuser)],
    response_model=PaginatedListResponse[dict]
)
async def get_all_user_active_backing_histroy(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int,
    items_per_page: int,
    user_address: str = Query(..., description="User's Public Address")
) -> dict:
    """
    - Returns only active user's backs
    """
    public_address = user_address.lower()
    user_data = await crud_predictions.get_multi_joined(
        db,
        schema_to_select=PredictionAndOpponents,
        nest_joins=True,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        joins_config=[
            JoinConfig(
                model=Opponent,
                join_on=Prediction.id == Opponent.prediction_id,
                schema_to_select=OpponentRead,
                relationship_type="one-to-many",
                filters={
                    "opponent_address": public_address
                }
            )
        ],
        settled=False
    )
    response: dict[str, Any] = paginated_response(
        crud_data=user_data,
        page=page,
        items_per_page=items_per_page
    )
    return response