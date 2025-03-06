from typing import Any, Dict, List, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from rich.console import Console

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


# Create singleton instance
mongodb_client = MongoDBClient()
