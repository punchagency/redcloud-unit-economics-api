from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.models.schemas import Category, CategoryResponse, HTTPError
from app.services.category_service import category_service

router = APIRouter()


@router.get(
    "",
    response_model=CategoryResponse,
    responses={400: {"model": HTTPError}, 500: {"model": HTTPError}},
    summary="Get Categories",
    description="Get a paginated list of Categories",
)
async def get_categories(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=1000, description="Items per page"),
    product_category: Optional[str] = Query(
        None, description="Filter by product category"
    ),
):
    """Get paginated list of Categories with optional product_category filter"""
    try:
        skip = (page - 1) * page_size
        result = await category_service.get_categories(
            skip=skip, limit=page_size, product_category=product_category
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{product_category}",
    response_model=CategoryResponse,
    responses={404: {"model": HTTPError}, 500: {"model": HTTPError}},
    summary="Get Category by Name",
    description="Get detailed information about a specific Category",
)
async def get_category(product_category: str):
    """Get a single Category by its product_category"""
    try:
        category = await category_service.get_category_by_name(product_category)
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f"Category with name {product_category} not found",
            )
        return JSONResponse(content=category)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
