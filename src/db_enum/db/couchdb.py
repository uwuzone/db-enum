import couchdb
from typing import Dict, Any
from ..db_interface import DBInterface
from ..logger import VerboseLogger


class CouchDBEnum(DBInterface):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "name": "CouchDB",
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
            server = couchdb.Server(f"http://{user}:{password}@{host}:{port}/")
            server.version()
            logger.info(f"Successfully connected to CouchDB at {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to CouchDB: {str(e)}")
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
        server = couchdb.Server(f"http://{user}:{password}@{host}:{port}/")

        result = {
            "type": "CouchDB",
            "kind": "document",
            "version": None,
            "databases": [],
            "database_info": [],
        }

        logger.info("Retrieving CouchDB version...")
        result["version"] = server.version()

        logger.info("Retrieving database list and information...")
        for db_name in server:
            result["databases"].append(db_name)
            db = server[db_name]
            db_info = db.info()
            result["database_info"].append(
                {
                    "name": db_name,
                    "doc_count": db_info.get("doc_count"),
                    "disk_size": db_info.get("disk_size"),
                    "update_seq": db_info.get("update_seq"),
                }
            )

        logger.info("CouchDB enumeration completed successfully")
        return result


check_connection = CouchDBEnum.check_connection
enumerate = CouchDBEnum.enumerate
get_info = CouchDBEnum.get_info
