from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.models.schemas import Brand, BrandResponse, HTTPError
from app.services.brand_service import brand_service

router = APIRouter()


@router.get(
    "",
    response_model=BrandResponse,
    responses={400: {"model": HTTPError}, 500: {"model": HTTPError}},
    summary="Get Brands",
    description="Get a paginated list of Brands",
)
async def get_brands(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=1000, description="Items per page"),
    brand_name: Optional[str] = Query(None, description="Filter by brand name"),
):
    """Get paginated list of Brands with optional brand name filter"""
    try:
        skip = (page - 1) * page_size
        result = await brand_service.get_brands(
            skip=skip, limit=page_size, brand_name=brand_name
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{brand_name}",
    response_model=BrandResponse,
    responses={404: {"model": HTTPError}, 500: {"model": HTTPError}},
    summary="Get Brand by Name",
    description="Get detailed information about a specific Brand",
)
async def get_brand(brand_name: str):
    """Get a single Brand by its name"""
    try:
        brand = await brand_service.get_brand_by_name(brand_name)
        if not brand:
            raise HTTPException(
                status_code=404, detail=f"Brand with name {brand_name} not found"
            )
        return JSONResponse(content=brand)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
