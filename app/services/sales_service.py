from datetime import datetime
from typing import Dict, List, Optional

from bson import ObjectId

from app.db.mongo_client import mongodb_client
from app.services.base import BaseService


class SalesService(BaseService):
    """Service for handling sales metrics operations"""

    @staticmethod
    def transform_aggregated_to_geojson(agg_doc: dict) -> dict:
        """
        Transforms an aggregated document (grouped by LGA) into a GeoJSON Feature.
        Expects that the aggregation has looked up the corresponding LGA document
        (from the 'lga_boundaries' collection) in the 'lga' field.
        """
        lga = agg_doc.get("lga", {})
        feature = {
            "type": "Feature",
            "id": str(lga.get("_id")),
            "properties": {
                "name": lga.get("lga_name", ""),
                "count": agg_doc.get("count"),
                "avgRetailerDensity": agg_doc.get("avgRetailerDensity"),
                "avgRevenue": agg_doc.get("avgRevenue"),
                "avgTTV": agg_doc.get("avgTTV"),
                "avgTransactionFrequency": agg_doc.get("avgTransactionFrequency"),
            },
            "geometry": lga.get("geometry"),
        }
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

            # Define the base aggregation pipeline.
            pipeline_base: List[Dict] = [
                {"$match": metrics_query},
                {
                    "$group": {
                        "_id": "$lga",
                        "count": {"$sum": 1},
                        "avgRetailerDensity": {"$avg": "$retailer_density"},
                        "avgRevenue": {"$avg": "$revenue_period_lga"},
                        "avgTTV": {"$avg": "$ttv_period_lga"},
                        "avgTransactionFrequency": {"$avg": "$transaction_frequency"},
                    }
                },
                {
                    "$lookup": {
                        "from": "lga_boundaries",
                        "localField": "_id",
                        "foreignField": "_id",
                        "as": "lga",
                    }
                },
                {"$unwind": "$lga"},
                {
                    "$project": {
                        "_id": 0,
                        "lga": 1,
                        "count": 1,
                        "avgRetailerDensity": 1,
                        "avgRevenue": 1,
                        "avgTTV": 1,
                        "avgTransactionFrequency": 1,
                    }
                },
            ]

            # Define the $facet stage for pagination.
            facet_stage = {
                "$facet": {
                    "data": [{"$skip": skip}, {"$limit": limit}],
                    "total": [{"$count": "total"}],
                }
            }

            # Combine pipeline base with facet.
            full_pipeline = pipeline_base + [facet_stage]

            # Build the aggregation using the AggregateBuilder.
            # (Assuming AggregateBuilder supports add_stage(stage) and exec() to run the pipeline.)
            agg_builder = mongodb_client.aggregate("state_boundaries_unit")
            for stage in full_pipeline:
                agg_builder.add_stage(stage)

            agg_result = await agg_builder.exec()

            # agg_result is a list; extract the first document.
            result_doc = (
                agg_result[0] if agg_result and isinstance(agg_result, list) else {}
            )
            total = (
                result_doc.get("total", [{}])[0].get("total", 0)
                if result_doc.get("total")
                else 0
            )
            aggregated_results = result_doc.get("data", [])

            # Transform each aggregated document into a GeoJSON Feature.
            aggregated_features = [
                SalesService.transform_aggregated_to_geojson(doc)
                for doc in aggregated_results
            ]

            result = {
                "data": aggregated_features,
                "total": total,
                "page": skip // limit + 1 if limit > 0 else 1,
                "page_size": limit,
            }

            await SalesService.set_cached_data(cache_key, result)
            return result

        except Exception as e:
            raise Exception(f"Error fetching sales metrics: {str(e)}")


# Create singleton instance
sales_service = SalesService()
