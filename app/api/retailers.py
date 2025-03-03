from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import HTTPError, RetailerMetrics
from app.services.retailer_service import retailer_service

router = APIRouter()


@router.get(
    "/search",
    response_model=List[RetailerMetrics],
    responses={
        400: {
            "description": "Invalid search query",
            "model": HTTPError
        },
        500: {
            "description": "Internal server error",
            "model": HTTPError
        }
    },
    summary="Search Retailers",
    description="Search retailers by name with optional city filter. Returns a list of matching retailers with their metrics."
)
async def search_retailers(
    q: str = Query(
        ...,
        min_length=2,
        description="Search query - minimum 2 characters",
        example="Electronics"
    ),
    city: Optional[str] = Query(
        None,
        description="Filter by city name",
        example="Lagos"
    ),
):
    """Search retailers by name with optional city filter"""
    try:
        results = await retailer_service.search_retailers(q, city)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{seller_id}",
    response_model=RetailerMetrics,
    responses={
        404: {
            "description": "Retailer not found",
            "model": HTTPError
        },
        500: {
            "description": "Internal server error",
            "model": HTTPError
        }
    },
    summary="Get Retailer Metrics",
    description="Returns detailed metrics for a specific retailer including revenue, orders, and location data"
)
async def get_retailer_metrics(seller_id: int):
    """Get metrics for a specific retailer"""
    metrics = await retailer_service.get_retailer_metrics(seller_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Retailer not found")
    return metrics
