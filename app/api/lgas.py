from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.models.schemas import LGA, HTTPError, LGAResponse
from app.services.lga_service import lga_service

router = APIRouter()


@router.get(
    "",
    response_model=LGAResponse,
    responses={400: {"model": HTTPError}, 500: {"model": HTTPError}},
    summary="Get LGAs",
    description="Get a paginated list of Local Government Areas (LGAs)",
)
async def get_lgas(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=1000, description="Items per page"),
    state_code: Optional[str] = Query(None, description="Filter by state code"),
):
    """Get paginated list of LGAs with optional state filter"""
    try:
        skip = (page - 1) * page_size
        result = await lga_service.get_lgas(
            skip=skip, limit=page_size, state_code=state_code
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{lga_code}",
    response_model=LGA,
    responses={404: {"model": HTTPError}, 500: {"model": HTTPError}},
    summary="Get LGA by Code",
    description="Get detailed information about a specific LGA",
)
async def get_lga(lga_code: str):
    """Get a single LGA by its code"""
    try:
        lga = await lga_service.get_lga_by_code(lga_code)
        if not lga:
            raise HTTPException(
                status_code=404, detail=f"LGA with code {lga_code} not found"
            )
        return JSONResponse(content=lga)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
