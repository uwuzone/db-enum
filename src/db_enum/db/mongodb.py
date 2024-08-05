from pymongo import MongoClient

# from pymongo.errors import ConnectionFailure
from typing import Dict, Any
from ..db_interface import DBInterface
from ..logger import VerboseLogger


class MongoDBEnum(DBInterface):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "name": "MongoDB",
            "kind": "document",
        }

    @staticmethod
    def check_connection(
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        logger: VerboseLogger,
    ) -> bool:
        try:
            client = MongoClient(
                f"mongodb://{user}:{password}@{host}:{port}/{database or ''}"
            )
            client.admin.command("ismaster")
            client.close()
            logger.info(f"Successfully connected to MongoDB at {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False

    @staticmethod
    def enumerate(
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        logger: VerboseLogger,
    ) -> Dict[str, Any]:
        client = MongoClient(
            f"mongodb://{user}:{password}@{host}:{port}/{database or ''}"
        )

        result = {
            "type": "MongoDB",
            "kind": "document",
            "version": None,
            "databases": [],
            "collections": [],
        }

        logger.info("Retrieving MongoDB version...")
        server_info = client.server_info()
        result["version"] = server_info.get("version")

        logger.info("Retrieving database list...")
        result["databases"] = client.list_database_names()

        logger.info("Retrieving collection information...")
        for db_name in result["databases"]:
            db = client[db_name]
            for collection_name in db.list_collection_names():
                # collection = db[collection_name]
                stats = db.command("collstats", collection_name)
                result["collections"].append(
                    {
                        "database": db_name,
                        "name": collection_name,
                        "document_count": stats.get("count"),
                        "size_bytes": stats.get("size"),
                    }
                )

        client.close()
        logger.info("MongoDB enumeration completed successfully")
        return result


check_connection = MongoDBEnum.check_connection
enumerate = MongoDBEnum.enumerate
get_info = MongoDBEnum.get_info
