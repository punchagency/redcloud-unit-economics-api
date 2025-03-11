from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.models.schemas import State, HTTPError, StateResponse
from app.services.state_service import state_service

router = APIRouter()


@router.get(
    "",
    response_model=StateResponse,
    responses={400: {"model": HTTPError}, 500: {"model": HTTPError}},
    summary="Get States",
    description="Get a paginated list of States",
)
async def get_lgas(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=1000, description="Items per page"),
    state_code: Optional[str] = Query(None, description="Filter by state code"),
):
    """Get paginated list of LGAs with optional state filter"""
    try:
        skip = (page - 1) * page_size
        result = await state_service.get_states(
            skip=skip, limit=page_size, state_code=state_code
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{state_code}",
    response_model=State,
    responses={404: {"model": HTTPError}, 500: {"model": HTTPError}},
    summary="Get State by Code",
    description="Get detailed information about a specific State",
)
async def get_state(state_code: str):
    """Get a single State by its code"""
    try:
        state = await state_service.get_state_by_code(state_code)
        if not state:
            raise HTTPException(
                status_code=404, detail=f"State with code {state_code} not found"
            )
        return JSONResponse(content=state)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
