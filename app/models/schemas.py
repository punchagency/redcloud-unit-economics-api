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
                "period_name": "001_007_2022",
            }
        }


class SalesMetrics(BaseModel):
    """Schema for sales metrics by state/LGA"""

    id: Optional[str] = Field(None, alias="_id")
    lga: str = Field(..., description="LGA ObjectId reference")
    state: str = Field(..., description="State ObjectId reference")
    date: str = Field(..., description="Period ObjectId reference")
    revenue_period_lga: float | None
    ttv_period_lga: float | None
    retailer_density: float | int | str | None
    transaction_frequency: float | int | str | None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "67c97d9f5e9a7a0da499bda4",
                "lga": "67c85d3f82e815e4ed9c613a",
                "state": "67c85980e71bd75bbbb1d1b1",
                "date": "67c879945e9a7a0da4997d35",
                "revenue_period_lga": 4.62,
                "ttv_period_lga": 230.84,
                "retailer_density": 10,
                "transaction_frequency": 2,
            }
        }


class SalesMetricsResponse(BaseModel):
    """Response schema for sales metrics endpoints"""

    data: list[SalesMetrics]
    total: int
    page: Optional[int] = None
    page_size: Optional[int] = None


class State(BaseModel):
    """Schema for State data"""

    id: Optional[str] = Field(None, alias="_id", description="MongoDB ObjectId")
    state_name: str = Field(..., description="Name of the state")
    state_code: str = Field(
        ...,
        description="Unique code for the state (e.g., 'NG001')",
        pattern="^NG\\d{3}$",
    )
    country_name: str = Field(..., description="Name of the country")
    geometry: Geometry = Field(
        ..., description="GeoJSON MultiPolygon geometry of the state"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "67c85980e71bd75bbbb1d1b1",
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


class StateResponse(BaseModel):
    """Response schema for state endpoints"""

    data: List[State] = Field(..., description="List of state records")
    total: int = Field(..., description="Total number of records")
    page: Optional[int] = Field(None, description="Current page number")
    page_size: Optional[int] = Field(None, description="Number of records per page")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
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


class Brand(BaseModel):
    """Schema for brand data"""

    id: str = Field(None, alias="_id", description="MongoDB ObjectId")
    brand_name: str = Field(..., description="Name of the brand")

    class Config:
        json_schema_extra = {
            "example": {"id": "67d43b1f48b591196ff405d7", "brand_name": "Sunlight"}
        }


class BrandMetrics(BaseModel):
    """Schema for brand boundaries data"""

    id: str = Field(None, alias="_id", description="Brand boundary ID")
    lga_id: str = Field(..., description="LGA ID")
    state_id: str = Field(..., description="State ID")
    date_id: str = Field(..., description="Date ID")
    brand_id: str = Field(..., description="Brand ID")
    revenue_period_lga: float = Field(..., description="Revenue for LGA in period")
    ttv_period_lga: float = Field(
        ..., description="Total transaction value for LGA in period"
    )
    retailer_density: int = Field(..., description="Density of retailers")
    transaction_frequency: int = Field(..., description="Frequency of transactions")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "67d444e848b591196ff4095b",
                "lga_id": "67c85d7782e815e4ed9c625f",
                "state_id": "67c8597be71bd75bbbb1d196",
                "date_id": "67c879945e9a7a0da4997d96",
                "brand_id": "67d43b1f48b591196ff405da",
                "revenue_period_lga": 467.55,
                "ttv_period_lga": 31170.00,
                "retailer_density": 2,
                "transaction_frequency": 5,
            }
        }


class Category(BaseModel):
    id: str = Field(..., description="Unique identifier for the category")
    product_category: str = Field(..., description="Name of the category")
    # Add other fields if necessary


class CategoryResponse(BaseModel):
    """Schema for paginated category response"""

    data: List[Category]
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "id": "67d43b1f48b591196ff405d7",
                        "product_category": "Electronics",
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 10,
            }
        }


class BrandResponse(BaseModel):
    """Schema for paginated brand response"""

    data: list[Brand]
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [{"id": "67d43b1f48b591196ff405d7", "brand_name": "Sunlight"}],
                "total": 1,
                "page": 1,
                "page_size": 10,
            }
        }


class BrandMetricsResponse(BaseModel):
    """Response schema for sales metrics endpoints"""

    data: list[BrandMetrics]
    total: int
    page: Optional[int] = None
    page_size: Optional[int] = None
