from elasticsearch import Elasticsearch
from typing import Dict, Any
from ..db_interface import DBInterface
from ..logger import VerboseLogger


class ElasticsearchEnum(DBInterface):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "name": "Elasticsearch",
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
            es = Elasticsearch([f"http://{host}:{port}"], http_auth=(user, password))
            if es.ping():
                logger.info(f"Successfully connected to Elasticsearch at {host}:{port}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {str(e)}")
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
        try:
            es = Elasticsearch([f"http://{host}:{port}"], http_auth=(user, password))

            result = {
                "type": "Elasticsearch",
                "kind": "document",
                "version": None,
                "indices": [],
            }

            logger.info("Retrieving Elasticsearch version...")
            info = es.info()
            result["version"] = info.get("version", {}).get("number")

            logger.info("Retrieving indices information...")
            indices = es.cat.indices(format="json")
            for index in indices:
                index_stats = es.indices.stats(index=index["index"])
                result["indices"].append(
                    {
                        "name": index["index"],
                        "doc_count": index["docs.count"],
                        "size_bytes": index["store.size"],
                        "primary_shards": index_stats["_all"]["primaries"]["docs"][
                            "count"
                        ],
                        "replica_shards": index_stats["_all"]["total"]["docs"]["count"]
                        - index_stats["_all"]["primaries"]["docs"]["count"],
                    }
                )

            logger.info("Elasticsearch enumeration completed successfully")
            return result

        except Exception as e:
            logger.error(f"Error enumerating Elasticsearch: {str(e)}")
            return {"error": str(e)}


check_connection = ElasticsearchEnum.check_connection
enumerate = ElasticsearchEnum.enumerate
get_info = ElasticsearchEnum.get_info
