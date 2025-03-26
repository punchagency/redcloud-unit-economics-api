from typing import Dict, Optional

from app.db.mongo_client import mongodb_client
from app.services.base import BaseService


class BrandService(BaseService):
    """Service for handling Brand operations"""

    @staticmethod
    async def get_brands(
        skip: int = 0, limit: int = 10, brand_name: Optional[str] = None
    ) -> Dict:
        """
        Get a paginated list of brands with optional brand name filter.

        Args:
            skip (int): Number of records to skip
            limit (int): Number of records to return
            brand_name (Optional[str]): Filter by brand name

        Returns:
            Dict: Paginated list of LGAs and total count
        """
        try:
            # Build cache key based on parameters
            cache_key = f"brands_list_{skip}_{limit}_{brand_name}"
            cached_data = await BrandService.get_cached_data(cache_key)
            if cached_data:
                return cached_data

            # Build query
            query = {}
            query["brand_name"] = {"$nin": [None, "-"]}
            if brand_name:
                query["brand_name"] = brand_name

            # Get total count
            total = len(await mongodb_client.find_many("brands", query))

            # Get paginated results
            brands = await mongodb_client.find_many(
                collection_name="brands",
                query=query,
                skip=skip,
                limit=limit,
                sort=[("brand_name", 1)],
            )

            # Serialize MongoDB documents
            serialized_brands = [
                BrandService.serialize_mongodb_doc(brand) for brand in brands
            ]

            result = {
                "data": serialized_brands,
                "total": total,
                "page": skip // limit + 1 if limit > 0 else 1,
                "page_size": limit,
            }

            # Cache the results
            await BrandService.set_cached_data(cache_key, result)
            return result

        except Exception as e:
            raise Exception(f"Error fetching brands: {str(e)}")

    @staticmethod
    async def get_brand_by_name(brand_name: str) -> Optional[Dict]:
        """
        Get a single brand by its name.

        Args:
            brand_name (str): The unique name of the brand

        Returns:
            Optional[Dict]: Brand data if found, None otherwise
        """
        try:
            # Check cache first
            cache_key = f"brand_{brand_name}"
            cached_data = await BrandService.get_cached_data(cache_key)
            if cached_data:
                return cached_data

            brand = await mongodb_client.find_one(
                collection_name="brands", query={"brand_name": brand_name}
            )
            if brand:
                serialized_brand = BrandService.serialize_mongodb_doc(brand)
                # Cache the result
                await BrandService.set_cached_data(cache_key, serialized_brand)
                return serialized_brand
            return None
        except Exception as e:
            raise Exception(f"Error fetching brand: {str(e)}")


# Create singleton instance
brand_service = BrandService()
