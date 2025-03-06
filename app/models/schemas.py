from datetime import datetime
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field


class HTTPError(BaseModel):
    detail: str


class CityResponse(BaseModel):
    city: str

    class Config:
        json_schema_extra = {"example": {"city": "Lagos"}}


class RetailerMetrics(BaseModel):
    seller_id: str | int | None
    seller_name: str | None
    store_name: str | None
    internal_seller_latitude: float | None
    internal_seller_longitude: float | None
    gross_ttv_usd: float | None
    revenue_usd: float | None
    total_orders: int | None
    product_categories: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "seller_id": "12345",
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


class Geometry(BaseModel):
    """Schema for GeoJSON MultiPolygon geometry"""

    type: Literal["MultiPolygon"] = Field(..., description="GeoJSON geometry type")
    coordinates: List[List[List[List[float]]]] = Field(
        ..., description="Array of polygon coordinates in [longitude, latitude] format"
    )


class LGABoundary(BaseModel):
    """Schema for Local Government Area (LGA) data"""

    id: Optional[str] = Field(None, alias="_id", description="MongoDB ObjectId")
    lga_name: str = Field(..., description="Name of the Local Government Area")
    lga_code: str = Field(
        ...,
        description="Unique code for the LGA (e.g., 'NG001001')",
    )
    state_name: str = Field(..., description="Name of the state")
    state_code: str = Field(
        ...,
        description="Unique code for the state (e.g., 'NG001')",
    )
    country_name: str = Field(..., description="Name of the country")
    geometry: Geometry = Field(
        ..., description="GeoJSON MultiPolygon geometry of the LGA"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "67c85d0882e815e4ed9c6021",
                "lga_name": "Aba North",
                "lga_code": "NG001001",
                "state_name": "Abia",
                "state_code": "NG001",
                "country_name": "Nigeria",
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [7.401109, 5.081947],
                                [7.400133, 5.082370],
                                [7.398485, 5.082554],
                            ]
                        ]
                    ],
                },
            }
        }


class LGAResponse(BaseModel):
    """Response schema for LGA endpoints"""

    data: List[LGABoundary] = Field(..., description="List of LGA records")
    total: int = Field(..., description="Total number of records")
    page: Optional[int] = Field(None, description="Current page number")
    page_size: Optional[int] = Field(None, description="Number of records per page")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "lga_name": "Aba North",
                        "lga_code": "NG001001",
                        "state_name": "Abia",
                        "state_code": "NG001",
                        "country_name": "Nigeria",
                        "geometry": {
                            "type": "MultiPolygon",
                            "coordinates": [
                                [
                                    [
                                        [7.401109, 5.081947],
                                        [7.400133, 5.082370],
                                        [7.398485, 5.082554],
                                    ]
                                ]
                            ],
                        },
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 10,
            }
        }


class LGA(BaseModel):
    """Schema for LGA boundary data without full geometry"""

    id: Optional[str] = Field(None, alias="_id", description="MongoDB ObjectId")
    lga_name: str = Field(..., description="Name of the Local Government Area")
    lga_code: str = Field(..., description="Unique code for the LGA")
    state_name: str = Field(..., description="Name of the state")
    state_code: str = Field(..., description="Unique code for the state")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "67c85d0882e815e4ed9c6021",
                "lga_name": "Aba North",
                "lga_code": "NG001001",
                "state_name": "Abia",
                "state_code": "NG001",
            }
        }


class Period(BaseModel):
    """Schema for time periods"""
    id: Optional[str] = Field(None, alias="_id")
    start_date: datetime
    end_date: datetime
    period_name: str

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "67c879945e9a7a0da4997d1e",
                "start_date": "2022-01-01T00:00:00Z",
                "end_date": "2022-01-07T23:59:59Z",
                "period_name": "001_007_2022"
            }
        }


class SalesMetrics(BaseModel):
    """Schema for sales metrics by state/LGA"""
    id: Optional[str] = Field(None, alias="_id")
    lga: str = Field(..., description="LGA ObjectId reference")
    state: str = Field(..., description="State ObjectId reference")
    date: str = Field(..., description="Period ObjectId reference")
    revenue_period_lga: float
    ttv_period_lga: float

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "67c97d9f5e9a7a0da499bda4",
                "lga": "67c85d3f82e815e4ed9c613a",
                "state": "67c85980e71bd75bbbb1d1b1",
                "date": "67c879945e9a7a0da4997d35",
                "revenue_period_lga": 4.62,
                "ttv_period_lga": 230.84
            }
        }


class SalesMetricsResponse(BaseModel):
    """Response schema for sales metrics endpoints"""
    data: list[SalesMetrics]
    total: int
    page: Optional[int] = None
    page_size: Optional[int] = None
