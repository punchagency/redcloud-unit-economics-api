from fastapi import APIRouter, HTTPException

from app.models.schemas import HTTPError, NeighborhoodMetrics
from app.services.neighborhood_service import neighborhood_service

router = APIRouter()


@router.get(
    "/neighborhoods/{city_name}/{neighborhood_name}",
    response_model=NeighborhoodMetrics,
    responses={
        404: {
            "description": "Neighborhood not found",
            "model": HTTPError
        },
        500: {
            "description": "Internal server error",
            "model": HTTPError
        }
    },
    summary="Get Neighborhood Metrics",
    description="Returns detailed metrics for a specific neighborhood including retailer density, revenue, and individual retailer data"
)
async def get_neighborhood_metrics(city_name: str, neighborhood_name: str):
    """Get detailed metrics for a specific neighborhood"""
    metrics = await neighborhood_service.get_neighborhood_metrics(
        city_name, neighborhood_name
    )
    if not metrics:
        raise HTTPException(status_code=404, detail="Neighborhood not found")
    return metrics
