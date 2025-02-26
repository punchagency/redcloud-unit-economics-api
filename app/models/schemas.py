from datetime import datetime
from typing import List

from pydantic import BaseModel


class HTTPError(BaseModel):
    detail: str


class CityResponse(BaseModel):
    city: str

    class Config:
        json_schema_extra = {"example": {"city": "Lagos"}}


class RetailerMetrics(BaseModel):
    seller_id: int
    seller_name: str
    store_name: str
    internal_seller_latitude: float
    internal_seller_longitude: float
    gross_ttv_usd: float
    revenue_usd: float
    total_orders: int
    product_categories: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "seller_id": 12345,
                "seller_name": "John's Store",
                "store_name": "JS Electronics",
                "internal_seller_latitude": 9.0765,
                "internal_seller_longitude": 7.3986,
                "gross_ttv_usd": 150000.00,
                "revenue_usd": 45000.00,
                "total_orders": 1200,
                "product_categories": ["Electronics", "Accessories"],
            }
        }


class NeighborhoodMetrics(BaseModel):
    name: str
    boundaries: List[List[float]]  # GeoJSON-like coordinates
    avg_ttv_usd: float
    retailer_density: int
    avg_order_frequency: float
    total_revenue_usd: float
    retailers: List[RetailerMetrics]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ikeja",
                "boundaries": [[7.3956, 9.0765], [7.3986, 9.0785]],
                "avg_ttv_usd": 125000.00,
                "retailer_density": 45,
                "avg_order_frequency": 25.5,
                "total_revenue_usd": 2250000.00,
                "retailers": [],  # Omitted for brevity
            }
        }


class CityMetrics(BaseModel):
    city_name: str
    total_revenue_usd: float
    total_retailers: int
    avg_ttv_usd: float
    neighborhoods: List[NeighborhoodMetrics]
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "city_name": "Lagos",
                "total_revenue_usd": 15000000.00,
                "total_retailers": 1200,
                "avg_ttv_usd": 125000.00,
                "neighborhoods": [],  # Omitted for brevity
                "updated_at": "2024-01-01T00:00:00",
            }
        }
