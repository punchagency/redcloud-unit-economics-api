from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.models.schemas import HTTPError, SalesMetricsResponse
from app.services.sales_service import sales_service

router = APIRouter()


@router.get(
    "",
    response_model=SalesMetricsResponse,
    responses={400: {"model": HTTPError}, 500: {"model": HTTPError}},
    summary="Get Sales Metrics",
    description="Get sales metrics filtered by date range and/or location",
)
async def get_sales_metrics(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=1000, description="Items per page"),
    start_date: Optional[datetime] = Query(
        None, description="Filter by start date (ISO format)"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Filter by end date (ISO format)"
    ),
    lga_id: Optional[str] = Query(None, description="Filter by LGA ObjectId"),
    brand_id: Optional[str] = Query(None, description="Filter by Brand ObjectId"),
    state_id: Optional[str] = Query(None, description="Filter by State ObjectId"),
    product_category: Optional[str] = Query(None, description="Filter by product category")
):
    """Get sales metrics with optional filters"""
    try:
        skip = (page - 1) * page_size
        result = await sales_service.get_sales_metricsv2(
            skip=skip,
            limit=page_size,
            start_date=start_date,
            end_date=end_date,
            lga_id=lga_id,
            state_id=state_id,
            brand_id=brand_id,
            product_category=product_category
            
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
