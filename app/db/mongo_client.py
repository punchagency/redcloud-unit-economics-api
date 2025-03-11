from typing import Any, Dict, List, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from rich.console import Console
import asyncio

from app.core.config import settings

console = Console()


class MongoDBClient:
    """
    MongoDB client singleton for database operations.
    Provides connection pooling and query execution.
    """

    def __init__(self):
        """Initialize MongoDB client with configuration."""
        try:
            self.client: MongoClient = MongoClient(
                settings.MONGODB_URI,
                connect=False,  # Defer connection until first operation
            )
            self.db: Database = self.client[settings.MONGODB_DB]
            # Test connection
            self.client.server_info()
            console.log("[green]MongoDB connection successful[/green]")
        except Exception as e:
            console.log(f"[red]MongoDB connection failed: {str(e)}[/red]")
            raise

    def get_collection(self, collection_name: str) -> Collection:
        """
        Get a MongoDB collection by name.

        Args:
            collection_name (str): Name of the collection

        Returns:
            Collection: MongoDB collection object
        """
        return self.db[collection_name]

    async def retrieve_all(
        self, collection_name: str, limit: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all documents from the specified collection.

        Args:
            collection_name (str): Name of the collection
            limit (int, optional): Maximum number of documents to return. Defaults to 0 (no limit).

        Returns:
            List[Dict[str, Any]]: List of all documents in the collection
        """
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find({})
            if limit > 0:
                cursor = cursor.limit(limit)
            documents = list(cursor)
            return documents
        except Exception as e:
            console.log(f"[red]Error in retrieve_all: {str(e)}[/red]")
            raise

    async def find_one(
        self, collection_name: str, query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Find a single document in the specified collection.

        Args:
            collection_name (str): Name of the collection
            query (Dict[str, Any]): Query filter

        Returns:
            Optional[Dict[str, Any]]: Found document or None
        """
        try:
            collection = self.get_collection(collection_name)
            return collection.find_one(query)
        except Exception as e:
            console.log(f"[red]Error in find_one: {str(e)}[/red]")
            raise

    async def find_many(
        self,
        collection_name: str,
        query: Dict[str, Any],
        limit: int = 0,
        skip: int = 0,
        sort: Optional[List[tuple]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find multiple documents in the specified collection.

        Args:
            collection_name (str): Name of the collection
            query (Dict[str, Any]): Query filter
            limit (int, optional): Maximum number of documents. Defaults to 0 (no limit).
            skip (int, optional): Number of documents to skip. Defaults to 0.
            sort (Optional[List[tuple]], optional): Sort specification. Defaults to None.

        Returns:
            List[Dict[str, Any]]: List of found documents
        """
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query).skip(skip)

            if limit > 0:
                cursor = cursor.limit(limit)

            if sort:
                cursor = cursor.sort(sort)

            return list(cursor)
        except Exception as e:
            console.log(f"[red]Error in find_many: {str(e)}[/red]")
            raise

    async def insert_one(self, collection_name: str, document: Dict[str, Any]) -> str:
        """
        Insert a single document into the specified collection.

        Args:
            collection_name (str): Name of the collection
            document (Dict[str, Any]): Document to insert

        Returns:
            str: Inserted document ID
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            console.log(f"[red]Error in insert_one: {str(e)}[/red]")
            raise

    async def update_one(
        self,
        collection_name: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> bool:
        """
        Update a single document in the specified collection.

        Args:
            collection_name (str): Name of the collection
            query (Dict[str, Any]): Query filter
            update (Dict[str, Any]): Update operations
            upsert (bool, optional): Create if not exists. Defaults to False.

        Returns:
            bool: True if document was updated
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_one(query, update, upsert=upsert)
            return result.modified_count > 0
        except Exception as e:
            console.log(f"[red]Error in update_one: {str(e)}[/red]")
            raise

    async def delete_one(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """
        Delete a single document from the specified collection.

        Args:
            collection_name (str): Name of the collection
            query (Dict[str, Any]): Query filter

        Returns:
            bool: True if document was deleted
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            console.log(f"[red]Error in delete_one: {str(e)}[/red]")
            raise

    def query(self, collection_name: str, query: Dict[str, Any] = {}) -> "QueryBuilder":
        """
        Start a chainable query on a given collection.
        """
        return QueryBuilder(self, collection_name, query)

    def aggregate(self, collection_name: str) -> "AggregateBuilder":
        """
        Start a chainable aggregation on a given collection.
        """
        return AggregateBuilder(self, collection_name)


class AggregateBuilder:
    """
    A chainable aggregate builder that supports adding aggregation stages.
    You can chain stages like $match, $group, $sort, etc.
    """

    def __init__(self, mongodb_client: MongoDBClient, collection_name: str):
        self.mongodb_client = mongodb_client
        self.collection = mongodb_client.get_collection(collection_name)
        self.pipeline: List[Dict[str, Any]] = []

    def match(self, criteria: Dict[str, Any]) -> "AggregateBuilder":
        self.pipeline.append({"$match": criteria})
        return self

    def group(self, group_spec: Dict[str, Any]) -> "AggregateBuilder":
        self.pipeline.append({"$group": group_spec})
        return self

    def sort(self, sort_spec: Dict[str, Any]) -> "AggregateBuilder":
        self.pipeline.append({"$sort": sort_spec})
        return self

    def project(self, projection: Dict[str, Any]) -> "AggregateBuilder":
        self.pipeline.append({"$project": projection})
        return self

    def skip(self, skip: int) -> "AggregateBuilder":
        self.pipeline.append({"$skip": skip})
        return self

    def limit(self, limit: int) -> "AggregateBuilder":
        self.pipeline.append({"$limit": limit})
        return self

    def add_stage(self, stage: Dict[str, Any]) -> "AggregateBuilder":
        """
        Add a custom aggregation stage.
        """
        self.pipeline.append(stage)
        return self

    async def exec(self) -> List[Dict[str, Any]]:
        def _aggregate():
            return list(self.collection.aggregate(self.pipeline))

        return await asyncio.to_thread(_aggregate)


class QueryBuilder:
    """
    A chainable query builder that supports methods such as limit, skip, sort, and populate.
    The populate method replaces a field's reference (e.g., an ObjectID) with the actual document.
    """

    def __init__(
        self,
        mongodb_client: MongoDBClient,
        collection_name: str,
        query: Dict[str, Any] = {},
    ):
        self.mongodb_client = mongodb_client
        self.collection = mongodb_client.get_collection(collection_name)
        self.query = query
        self._limit = 0
        self._skip = 0
        self._sort = None
        self._populate_fields: List[str] = []

    def limit(self, limit: int) -> "QueryBuilder":
        self._limit = limit
        return self

    def skip(self, skip: int) -> "QueryBuilder":
        self._skip = skip
        return self

    def sort(self, sort: List[tuple]) -> "QueryBuilder":
        self._sort = sort
        return self

    def populate(
        self, field: str, target_collection: Optional[str] = None
    ) -> "QueryBuilder":
        """
        Specify a field to populate.
        Optionally, provide the target collection name.
        If target_collection is None, defaults to the field name.
        """
        self._populate_fields.append((field, target_collection or field))
        return self

    async def exec(self) -> List[Dict[str, Any]]:
        # Wrap the synchronous find operation in asyncio.to_thread
        def get_documents():
            cursor = self.collection.find(self.query)
            if self._skip:
                cursor = cursor.skip(self._skip)
            if self._limit:
                cursor = cursor.limit(self._limit)
            if self._sort:
                cursor = cursor.sort(self._sort)
            return list(cursor)

        documents = await asyncio.to_thread(get_documents)
        if not documents:
            return documents

        # Batch populate for each specified field.
        for field, target_coll in self._populate_fields:
            ref_ids = set()
            for doc in documents:
                if field in doc:
                    value = doc[field]
                    if isinstance(value, list):
                        ref_ids.update(value)
                    else:
                        ref_ids.add(value)
            if not ref_ids:
                continue

            ref_collection = self.mongodb_client.get_collection(target_coll)

            def get_fetched_docs():
                return list(ref_collection.find({"_id": {"$in": list(ref_ids)}}))

            fetched_docs = await asyncio.to_thread(get_fetched_docs)
            fetched_mapping = {d["_id"]: d for d in fetched_docs}

            for doc in documents:
                if field in doc:
                    value = doc[field]
                    if isinstance(value, list):
                        doc[field] = [fetched_mapping.get(v, v) for v in value]
                    else:
                        doc[field] = fetched_mapping.get(value, value)
        return documents

        # Populate each document for every specified field.
        # for doc in documents:
        #     for field in self._populate_fields:
        #         if field in doc:
        #             ref_id = doc[field]
        #             ref_collection = self.mongodb_client.get_collection(field)
        #             populated_doc = ref_collection.find_one({"_id": ref_id})
        #             doc[field] = populated_doc

        # return documents

    async def exec_one(self) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one(self.query)
        if not doc:
            return doc

        for field, target_coll in self._populate_fields:
            if field in doc:
                value = doc[field]
                ref_collection = self.mongodb_client.get_collection(target_coll)
                if isinstance(value, list):
                    fetched_docs = await ref_collection.find(
                        {"_id": {"$in": value}}
                    ).to_list(length=len(value))
                    fetched_mapping = {d["_id"]: d for d in fetched_docs}
                    doc[field] = [fetched_mapping.get(v, v) for v in value]
                else:
                    populated_doc = await ref_collection.find_one({"_id": value})
                    doc[field] = populated_doc if populated_doc else value
        return doc

        # doc = self.collection.find_one(self.query)
        # if doc:
        #     for field in self._populate_fields:
        #         if field in doc:
        #             ref_id = doc[field]
        #             ref_collection = self.mongodb_client.get_collection(field)
        #             populated_doc = ref_collection.find_one({"_id": ref_id})
        #             doc[field] = populated_doc
        # return doc


# Create singleton instance
mongodb_client = MongoDBClient()
