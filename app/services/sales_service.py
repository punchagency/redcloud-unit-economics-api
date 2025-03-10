from datetime import datetime
from typing import Dict, List, Optional

from bson import ObjectId

from app.db.mongo_client import mongodb_client
from app.services.base import BaseService


class SalesService(BaseService):
    """Service for handling sales metrics operations"""

    @staticmethod
    def transform_to_geojson(metric: dict) -> dict:
        """
        Transforms a sales metric document into a GeoJSON Feature.
        Assumes the document has a populated 'lga' field that contains geometry and a name.
        """
        lga_info = metric.get("lga", {})
        feature = {
            "type": "Feature",
            "id": str(metric.get("_id")),
            "properties": {
                "name": lga_info.get("lga_name", ""),  # use lga_name as feature name
                "density": metric.get(
                    "retailer_density"
                ),  # use retailer_density as density
                "revenue": metric.get("revenue_period_lga"),
                "ttv": metric.get("ttv_period_lga"),
                "transaction_frequency": metric.get("transaction_frequency"),
            },
            "geometry": lga_info.get(
                "geometry"
            ),  # use the geometry from the lga document
        }
        return feature

    @staticmethod
    def serialize_geojson(metric: dict) -> dict:
        """
        Transforms a MongoDB document into the desired GeoJSON Feature shape,
        then delegates the JSON conversion to the BaseService's serializer.
        """
        feature = SalesService.transform_to_geojson(metric)
        return BaseService.serialize_mongodb_doc(feature)

    @staticmethod
    async def get_sales_metrics(
        skip: int = 0,
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        lga_id: Optional[str] = None,
        state_id: Optional[str] = None,
    ) -> Dict:
        """
        Get sales metrics filtered by date range and/or location.

        Args:
            skip: Number of records to skip
            limit: Number of records to return
            start_date: Optional start date filter
            end_date: Optional end date filter
            lga_id: Optional LGA ObjectId
            state_id: Optional State ObjectId

        Returns:
            Dict containing paginated sales metrics
        """
        try:
            # Build cache key
            cache_key = f"sales_metrics_{skip}_{limit}_{start_date}_{end_date}_{lga_id}_{state_id}"
            cached_data = await SalesService.get_cached_data(cache_key)
            if cached_data:
                return cached_data

            # Get period IDs matching date range
            period_query = {}
            if start_date:
                period_query["start_date"] = {"$gte": start_date}
            if end_date:
                period_query["end_date"] = {"$lte": end_date}

            if period_query:
                periods = await mongodb_client.find_many(
                    collection_name="periods", query=period_query
                )
                period_ids = [str(period["_id"]) for period in periods]
            else:
                period_ids = []

            # Build metrics query
            metrics_query = {}
            if period_ids:
                metrics_query["date"] = {"$in": [ObjectId(pid) for pid in period_ids]}
            if lga_id:
                metrics_query["lga"] = ObjectId(lga_id)
            if state_id:
                metrics_query["state"] = ObjectId(state_id)

            # Get total count
            total = len(
                await mongodb_client.find_many("state_boundaries_unit", metrics_query)
            )

            # Get paginated results
            # metrics = await mongodb_client.find_many(
            #     collection_name="state_boundaries_unit",
            #     query=metrics_query,
            #     skip=skip,
            #     limit=limit,
            #     sort=[("date", 1)],
            # )

            # Retrieve paginated results using the async query builder with population for "lga"
            metrics = await (
                mongodb_client.query("state_boundaries_unit", metrics_query)
                .populate(
                    "lga", "lga_boundaries"
                )  # Explicitly map "lga" to "lga_boundaries" collection.
                .skip(skip)
                .limit(limit)
                .sort([("date", 1)])
                .exec()
            )

            # # Serialize results
            # serialized_metrics = [
            #     SalesService.serialize_mongodb_doc(metric) for metric in metrics
            # ]

            # Delegate JSON serialization to the BaseService by calling our helper.
            serialized_metrics = [
                SalesService.serialize_geojson(metric) for metric in metrics
            ]

            result = {
                "data": serialized_metrics,
                "total": total,
                "page": skip // limit + 1 if limit > 0 else 1,
                "page_size": limit,
            }

            # Cache results
            await SalesService.set_cached_data(cache_key, result)
            return result

        except Exception as e:
            raise Exception(f"Error fetching sales metrics: {str(e)}")


# Create singleton instance
sales_service = SalesService()
