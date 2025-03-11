from typing import Dict, Optional

from app.db.mongo_client import mongodb_client
from app.services.base import BaseService


class StateService(BaseService):
    """Service for handling State operations"""

    @staticmethod
    async def get_states(
        skip: int = 0, limit: int = 10, state_code: Optional[str] = None
    ) -> Dict:
        """
        Get a paginated list of states with optional state code filter.

        Args:
            skip (int): Number of records to skip
            limit (int): Number of records to return
            state_code (Optional[str]): Filter by state code

        Returns:
            Dict: Paginated list of LGAs and total count
        """
        try:
            # Build cache key based on parameters
            cache_key = f"states_list_{skip}_{limit}_{state_code}"
            cached_data = await StateService.get_cached_data(cache_key)
            if cached_data:
                return cached_data

            # Build query
            query = {}
            if state_code:
                query["state_code"] = state_code

            # Get total count
            total = len(await mongodb_client.find_many("state_boundaries", query))

            # Get paginated results
            states = await mongodb_client.find_many(
                collection_name="state_boundaries",
                query=query,
                skip=skip,
                limit=limit,
                sort=[("state_name", 1)],
            )

            # Serialize MongoDB documents
            serialized_states = [StateService.serialize_mongodb_doc(state) for state in states]

            result = {
                "data": serialized_states,
                "total": total,
                "page": skip // limit + 1 if limit > 0 else 1,
                "page_size": limit,
            }

            # Cache the results
            await StateService.set_cached_data(cache_key, result)
            return result

        except Exception as e:
            raise Exception(f"Error fetching states: {str(e)}")

    @staticmethod
    async def get_state_by_code(state_code: str) -> Optional[Dict]:
        """
        Get a single state by its code.

        Args:
            state_code (str): The unique code of the state

        Returns:
            Optional[Dict]: State data if found, None otherwise
        """
        try:
            # Check cache first
            cache_key = f"state_{state_code}"
            cached_data = await StateService.get_cached_data(cache_key)
            if cached_data:
                return cached_data

            state = await mongodb_client.find_one(
                collection_name="state_boundaries", query={"state_code": state_code}
            )
            if state:
                serialized_state = StateService.serialize_mongodb_doc(state)
                # Cache the result
                await StateService.set_cached_data(cache_key, serialized_state)
                return serialized_state
            return None
        except Exception as e:
            raise Exception(f"Error fetching state: {str(e)}")


# Create singleton instance
state_service = StateService()
