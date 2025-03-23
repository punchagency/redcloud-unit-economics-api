from typing import Dict, Optional
from app.db.mongo_client import mongodb_client
from app.services.base import BaseService


class CategoryService(BaseService):
    """Service for handling Category operations"""

    @staticmethod
    async def get_categories(
        skip: int = 0, limit: int = 10, product_category: Optional[str] = None
    ) -> Dict:
        """
        Get a paginated list of categories with an optional partial product_category filter.
        Uses a single aggregation pipeline with $facet to get both the total count
        and paginated results in one DB call.
        """
        try:
            # Build cache key based on parameters
            cache_key = f"categories_list_{skip}_{limit}_{product_category}"
            cached_data = await CategoryService.get_cached_data(cache_key)
            if cached_data:
                return cached_data

            # Build query.
            # If a specific product_category is provided, filter by a partial match (case-insensitive);
            # otherwise, exclude documents where product_category is None or "-"
            query = {}
            if product_category:
                query["product_category"] = {
                    "$regex": product_category,
                    "$options": "i",
                }
            else:
                query["product_category"] = {"$nin": [None, "-"]}

            # Build the aggregation pipeline with $facet.
            pipeline = [
                {"$match": query},
                {
                    "$facet": {
                        "data": [
                            {"$sort": {"product_category": 1}},
                            {"$skip": skip},
                            {"$limit": limit},
                        ],
                        "total": [{"$count": "count"}],
                    }
                },
            ]

            # Use the existing AggregateBuilder.
            agg_builder = mongodb_client.aggregate("product_categories")
            for stage in pipeline:
                agg_builder.add_stage(stage)
            agg_result = await agg_builder.exec()

            # agg_result is expected to be a list with one document.
            result_doc = agg_result[0] if agg_result and len(agg_result) > 0 else {}
            total = (
                result_doc.get("total", [{}])[0].get("count", 0)
                if result_doc.get("total")
                else 0
            )
            categories = result_doc.get("data", [])

            # Serialize MongoDB documents.
            serialized_categories = [
                CategoryService.serialize_mongodb_doc(category)
                for category in categories
            ]

            result = {
                "data": serialized_categories,
                "total": total,
                "page": skip // limit + 1 if limit > 0 else 1,
                "page_size": limit,
            }

            # Cache the results.
            await CategoryService.set_cached_data(cache_key, result)
            return result

        except Exception as e:
            raise Exception(f"Error fetching categories: {str(e)}")

    @staticmethod
    async def get_category_by_name(product_category: str) -> Optional[Dict]:
        """
        Get a single category by its product_category.

        Args:
            product_category (str): The unique name of the category.

        Returns:
            Optional[Dict]: Category data if found, None otherwise.
        """
        try:
            # Check cache first
            cache_key = f"category_{product_category}"
            cached_data = await CategoryService.get_cached_data(cache_key)
            if cached_data:
                return cached_data

            category = await mongodb_client.find_one(
                collection_name="product_categories",
                query={"product_category": product_category},
            )
            if category:
                serialized_category = CategoryService.serialize_mongodb_doc(category)
                # Cache the result
                await CategoryService.set_cached_data(cache_key, serialized_category)
                return serialized_category
            return None
        except Exception as e:
            raise Exception(f"Error fetching category: {str(e)}")


# Create singleton instance
category_service = CategoryService()
