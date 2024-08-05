from neo4j import GraphDatabase
from typing import Dict, Any
from ..db_interface import DBInterface
from ..logger import VerboseLogger


class Neo4jEnum(DBInterface):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "name": "Neo4j",
            "kind": "graph",
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
            uri = f"neo4j://{host}:{port}"
            driver = GraphDatabase.driver(uri, auth=(user, password))
            with driver.session(database=database) as session:
                session.run("RETURN 1")
            driver.close()
            logger.info(f"Successfully connected to Neo4j at {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
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
        uri = f"neo4j://{host}:{port}"
        driver = GraphDatabase.driver(uri, auth=(user, password))

        result = {
            "type": "Neo4j",
            "kind": "graph",
            "version": None,
            "databases": [],
            "node_labels": [],
            "relationship_types": [],
        }

        with driver.session(database=database) as session:
            logger.info("Retrieving Neo4j version...")
            version_query = session.run(
                "CALL dbms.components() YIELD versions RETURN versions[0] as version"
            )
            result["version"] = version_query.single()["version"]

            logger.info("Retrieving database list...")
            db_query = session.run("SHOW DATABASES")
            result["databases"] = [record["name"] for record in db_query]

            logger.info("Retrieving node labels...")
            label_query = session.run("CALL db.labels()")
            result["node_labels"] = [record["label"] for record in label_query]

            logger.info("Retrieving relationship types...")
            rel_query = session.run("CALL db.relationshipTypes()")
            result["relationship_types"] = [
                record["relationshipType"] for record in rel_query
            ]

        driver.close()
        logger.info("Neo4j enumeration completed successfully")
        return result


check_connection = Neo4jEnum.check_connection
enumerate = Neo4jEnum.enumerate
get_info = Neo4jEnum.get_info
