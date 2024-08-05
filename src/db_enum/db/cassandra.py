from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from typing import Dict, Any
from ..db_interface import DBInterface
from ..logger import VerboseLogger


class CassandraEnum(DBInterface):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "name": "Cassandra",
            "kind": "wide-column",
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
            auth_provider = PlainTextAuthProvider(username=user, password=password)
            cluster = Cluster([host], port=port, auth_provider=auth_provider)
            session = cluster.connect()
            session.shutdown()
            cluster.shutdown()
            logger.info(f"Successfully connected to Cassandra at {host}:{port}")
            return True
        except Exception as e:
            logger.info(f"Failed to connect to Cassandra: {str(e)}")
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
        auth_provider = PlainTextAuthProvider(username=user, password=password)
        cluster = Cluster([host], port=port, auth_provider=auth_provider)
        session = cluster.connect()

        result = {
            "type": "Cassandra",
            "kind": "wide-column",
            "version": None,
            "keyspaces": [],
            "tables": [],
        }

        logger.info("Retrieving Cassandra version...")
        row = session.execute("SELECT release_version FROM system.local").one()
        result["version"] = row.release_version if row else "Unknown"

        logger.info("Retrieving keyspace and table information...")
        keyspaces = session.execute("SELECT keyspace_name FROM system_schema.keyspaces")
        for keyspace in keyspaces:
            result["keyspaces"].append(keyspace.keyspace_name)
            tables = session.execute(
                f"SELECT table_name FROM system_schema.tables WHERE keyspace_name = '{keyspace.keyspace_name}'"
            )
            for table in tables:
                result["tables"].append(
                    {"keyspace": keyspace.keyspace_name, "name": table.table_name}
                )

        session.shutdown()
        cluster.shutdown()
        logger.info("Cassandra enumeration completed successfully")
        return result


check_connection = CassandraEnum.check_connection
enumerate = CassandraEnum.enumerate
get_info = CassandraEnum.get_info
