from typing import List

from fastapi import APIRouter, HTTPException

from app.models.schemas import CityMetrics, CityResponse, HTTPError
from app.services.city_service import city_service

router = APIRouter()


@router.get(
    "/cities",
    response_model=List[CityResponse],
    responses={
        200: {
            "description": "List of available cities",
            "content": {
                "application/json": {
                    "example": [
                        {"city": "Lagos"},
                        {"city": "Abuja"},
                        {"city": "Port Harcourt"}
                    ]
                }
            },
        },
        500: {"description": "Internal server error", "model": HTTPError},
    },
    summary="Get Cities",
    description="Returns a list of all available cities in the system",
)
async def get_cities():
    """Get list of available cities"""
    return await city_service.get_cities()


@router.get(
    "/cities/{city_name}/metrics",
    response_model=CityMetrics,
    responses={
        404: {"description": "City not found", "model": HTTPError},
        500: {"description": "Internal server error", "model": HTTPError},
    },
    summary="Get City Metrics",
    description="Returns detailed metrics for a specific city including revenue, retailer count, and neighborhood data",
)
async def get_city_metrics(city_name: str):
    """Get metrics for a specific city"""
    metrics = await city_service.get_city_metrics(city_name)
    if not metrics:
        raise HTTPException(status_code=404, detail="City not found")
    return metrics
