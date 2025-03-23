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
        Transforms an aggregated document (grouped by LGA and product_category,
        and optionally brand) into a GeoJSON Feature.
        Expects that the aggregation has looked up the corresponding LGA document
        (from 'lga_boundaries') in the 'lga' field and product category details
        in the 'product_category' field.
        Optionally includes "brand_name" if brand data is present.
        """
        lga = agg_doc.get("lga", {})
        prod_cat = agg_doc.get("product_category", {})
        properties = {
            "name": lga.get("lga_name", ""),
            "product_category": prod_cat.get("product_category", ""),
            "count": agg_doc.get("count"),
            "avgRetailerDensity": agg_doc.get("avgRetailerDensity"),
            "avgRevenue": agg_doc.get("avgRevenue"),
            "avgTTV": agg_doc.get("avgTTV"),
            "avgTransactionFrequency": agg_doc.get("avgTransactionFrequency"),
        }
        brand = agg_doc.get("brand")
        if brand and isinstance(brand, dict) and brand.get("brand_name"):
            properties["brand_name"] = brand.get("brand_name")
        feature = {
            "type": "Feature",
            "id": str(lga.get("_id")),
            "properties": properties,
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
        brand_id: Optional[str] = None,
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
            brand_id: Optional Brand ObjectId.

        Returns:
            Dict containing paginated sales metrics
        """
        try:
            # Build cache key
            cache_key = f"sales_metrics_{skip}_{limit}_{start_date}_{end_date}_{lga_id}_{state_id}_{brand_id}"
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
            else:
                metrics_query["date"] = {"$exists": False}
            if lga_id:
                metrics_query["lga"] = ObjectId(lga_id)
            if state_id:
                metrics_query["state"] = ObjectId(state_id)
            if brand_id:
                metrics_query["brand"] = ObjectId(brand_id)

            # Define the base aggregation pipeline.
            # Build the group _id dynamically.
            group_id = {"lga": "$lga"}
            if brand_id:
                group_id["brand"] = "$brand"

            pipeline_base: List[Dict] = [
                {"$match": metrics_query},
                {
                    "$group": {
                        "_id": group_id,
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
                        "localField": "_id.lga",
                        "foreignField": "_id",
                        "as": "lga",
                    }
                },
                {"$unwind": "$lga"},
            ]

            # Append brand-related stages if a brand_id is provided.
            if brand_id:
                pipeline_base.extend(
                    [
                        {
                            "$lookup": {
                                "from": "brands",
                                "localField": "_id.brand",
                                "foreignField": "_id",
                                "as": "brand",
                            }
                        },
                        {"$unwind": "$brand"},
                    ]
                )

            # Build the project stage dynamically.
            project_stage = {
                "$project": {
                    "_id": 0,
                    "lga": 1,
                    "count": 1,
                    "avgRetailerDensity": 1,
                    "avgRevenue": 1,
                    "avgTTV": 1,
                    "avgTransactionFrequency": 1,
                }
            }
            if brand_id:
                project_stage["$project"]["brand"] = 1

            pipeline_base.append(project_stage)

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
            agg_builder = mongodb_client.aggregate("brand_boundaries_unit")
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

    @staticmethod
    async def get_sales_metricsv2(
        skip: int = 0,
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        lga_id: Optional[str] = None,
        state_id: Optional[str] = None,
        brand_id: Optional[str] = None,
        product_category: Optional[str] = None,
    ) -> Dict:
        """
        Get sales metrics from the 'brand_categories_boundaries_unit' collection filtered by date range,
        location, brand, and product category.

        In this collection, each document contains an 'items' array that may hold metrics
        for multiple product categories. This pipeline:
          1. Matches top-level filters (date, lga, state, brand).
          2. Unwinds the items array.
          3. Optionally filters on items.product_category if a product_category filter is provided.
          4. Groups by a composite key (lga and items.product_category, and brand if provided),
             aggregating metrics from each item.
          5. Looks up LGA details from 'lga_boundaries'.
          6. Looks up product category details from 'product_categories'.
          7. Optionally, if a brand filter is provided, looks up brand details from 'brands'.
          8. Projects only the required fields.
          9. Uses $facet to return both paginated data and the total count in a single DB call.
        """
        try:
            cache_key = ( 
                f"sales_metrics_v2_{skip}_{limit}_{start_date}_{end_date}_"
                f"{lga_id}_{state_id}_{brand_id}_{product_category}"
            )
            cached_data = await SalesService.get_cached_data(cache_key)
            if cached_data:
                return cached_data

            # Build period query
            period_query = {}
            if start_date:
                period_query["start_date"] = {"$gte": start_date}

            if end_date:
                period_query["end_date"] = {"$lte": end_date}

            if period_query:
                periods = await mongodb_client.find_many(
                    collection_name="periods", query=period_query
                )
                period_ids = [str(p["_id"]) for p in periods]
            else:
                period_ids = []

            # Build top-level query for the new collection.
            metrics_query = {}
            if period_ids:
                metrics_query["date"] = {"$in": [ObjectId(pid) for pid in period_ids]}


            if lga_id:
                metrics_query["lga"] = ObjectId(lga_id)

            if state_id:
                metrics_query["state"] = ObjectId(state_id)

            if brand_id:
                metrics_query["brand"] = ObjectId(brand_id)

            pipeline: List[Dict] = []

            # Stage 1: Match top-level fields.
            pipeline.append({"$match": metrics_query})

            # Stage 2: Unwind the items array.
            pipeline.append({"$unwind": "$items"})

            # Stage 3: If product_category filter is provided, match items.product_category.
            if product_category:
                pipeline.append(
                    {"$match": {"items.product_category": ObjectId(product_category)}}
                )

            # Stage 4: Group by composite key.
            # Always group by lga and items.product_category.
            group_id = {"lga": "$lga", "product_category": "$items.product_category"}
            if brand_id:
                group_id["brand"] = "$brand"

            pipeline.append(
                {
                    "$group": {
                        "_id": group_id,
                        "count": {"$sum": 1},
                        "avgRetailerDensity": {"$avg": "$items.retailer_density"},
                        "avgRevenue": {"$avg": "$items.revenue_period_lga"},
                        "avgTTV": {"$avg": "$items.ttv_period_lga"},
                        "avgTransactionFrequency": {
                            "$avg": "$items.transaction_frequency"
                        },
                    }
                }
            )

            # Stage 5: Lookup LGA details.
            pipeline.append(
                {
                    "$lookup": {
                        "from": "lga_boundaries",
                        "localField": "_id.lga",
                        "foreignField": "_id",
                        "as": "lga",
                    }
                }
            )
            pipeline.append({"$unwind": "$lga"})

            # Stage 6: Lookup product category details.
            pipeline.append(
                {
                    "$lookup": {
                        "from": "product_categories",
                        "localField": "_id.product_category",
                        "foreignField": "_id",
                        "as": "product_category",
                    }
                }
            )
            pipeline.append({"$unwind": "$product_category"})

            # Stage 7: If brand filter provided, lookup brand details.
            if brand_id:
                pipeline.append(
                    {
                        "$lookup": {
                            "from": "brands",
                            "localField": "_id.brand",
                            "foreignField": "_id",
                            "as": "brand",
                        }
                    }
                )
                pipeline.append({"$unwind": "$brand"})

            # Stage 8: Project the required fields.
            proj = {
                "$project": {
                    "_id": 0,
                    "lga": 1,
                    "product_category": 1,
                    "count": 1,
                    "avgRetailerDensity": 1,
                    "avgRevenue": 1,
                    "avgTTV": 1,
                    "avgTransactionFrequency": 1,
                }
            }
            if brand_id:
                proj["$project"]["brand"] = 1
            pipeline.append(proj)

            # Stage 9: Facet for pagination.
            pipeline.append(
                {
                    "$facet": {
                        "data": [{"$skip": skip}, {"$limit": limit}],
                        "total": [{"$count": "total"}],
                    }
                }
            )

            # Execute the aggregation using the existing AggregateBuilder.
            agg_builder = mongodb_client.aggregate("brand_category_boundaries_unit")
            for stage in pipeline:
                agg_builder.add_stage(stage)
                
            agg_result = await agg_builder.exec() 
            
          
            
            # agg_result is expected to be a list with one document.
            result_doc = agg_result[0] if agg_result and len(agg_result) > 0 else {}
            total = (result_doc.get("total", [{}])[0].get("total", 0)
                     if result_doc.get("total") else 0)
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
            raise Exception(f"Error fetching sales metrics v2: {str(e)}")


# Create singleton instance
sales_service = SalesService()
