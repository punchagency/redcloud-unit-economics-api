from typing import Dict, Optional

from app.db.mongo_client import mongodb_client
from app.services.base import BaseService


class LGAService(BaseService):
    """Service for handling Local Government Area (LGA) operations"""

    @staticmethod
    async def get_lgas(
        skip: int = 0, limit: int = 10, state_code: Optional[str] = None
    ) -> Dict:
        """
        Get a paginated list of LGAs with optional state filter.

        Args:
            skip (int): Number of records to skip
            limit (int): Number of records to return
            state_code (Optional[str]): Filter by state code

        Returns:
            Dict: Paginated list of LGAs and total count
        """
        try:
            # Build cache key based on parameters
            cache_key = f"lgas_list_{skip}_{limit}_{state_code}"
            cached_data = await LGAService.get_cached_data(cache_key)
            if cached_data:
                return cached_data

            # Build query
            query = {}
            if state_code:
                query["state_code"] = state_code

            # Get total count
            total = len(await mongodb_client.find_many("lga_boundaries", query))

            # Get paginated results
            lgas = await mongodb_client.find_many(
                collection_name="lga_boundaries",
                query=query,
                skip=skip,
                limit=limit,
                sort=[("state_name", 1), ("lga_name", 1)],
            )

            # Serialize MongoDB documents
            serialized_lgas = [LGAService.serialize_mongodb_doc(lga) for lga in lgas]

            result = {
                "data": serialized_lgas,
                "total": total,
                "page": skip // limit + 1 if limit > 0 else 1,
                "page_size": limit,
            }

            # Cache the results
            await LGAService.set_cached_data(cache_key, result)
            return result

        except Exception as e:
            raise Exception(f"Error fetching LGAs: {str(e)}")

    @staticmethod
    async def get_lga_by_code(lga_code: str) -> Optional[Dict]:
        """
        Get a single LGA by its code.

        Args:
            lga_code (str): The unique code of the LGA

        Returns:
            Optional[Dict]: LGA data if found, None otherwise
        """
        try:
            # Check cache first
            cache_key = f"lga_{lga_code}"
            cached_data = await LGAService.get_cached_data(cache_key)
            if cached_data:
                return cached_data

            lga = await mongodb_client.find_one(
                collection_name="lga_boundaries", query={"lga_code": lga_code}
            )
            if lga:
                serialized_lga = LGAService.serialize_mongodb_doc(lga)
                # Cache the result
                await LGAService.set_cached_data(cache_key, serialized_lga)
                return serialized_lga
            return None
        except Exception as e:
            raise Exception(f"Error fetching LGA: {str(e)}")


# Create singleton instance
lga_service = LGAService()
