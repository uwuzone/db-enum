import psycopg2
from psycopg2.extras import DictCursor
from typing import Dict, Any

from db_enum.logger import VerboseLogger

from ..db_interface import DBInterface


class PostgresEnum(DBInterface):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "name": "PostgreSQL",
            "kind": "sql",
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
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=database or "postgres",
            )
            conn.close()
            logger.info(f"Successfully connected to PostgreSQL at {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
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
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=database or "postgres",
            )
            cursor = conn.cursor(cursor_factory=DictCursor)

            result = {
                "type": "PostgreSQL",
                "kind": "sql",
                "version": None,
                "databases": [],
                "tables": [],
            }

            logger.info("Retrieving PostgreSQL version...")
            cursor.execute("SELECT version()")
            result["version"] = cursor.fetchone()[0]

            logger.info("Retrieving database list...")
            cursor.execute(
                "SELECT datname FROM pg_database WHERE datistemplate = false"
            )
            result["databases"] = [row[0] for row in cursor.fetchall()]

            logger.info("Retrieving table information...")
            cursor.execute(
                """
                SELECT schemaname, tablename, n_live_tup, pg_total_relation_size('"' || schemaname || '"."' || tablename || '"') as total_bytes
                FROM pg_stat_user_tables
            """
            )
            for row in cursor.fetchall():
                result["tables"].append(
                    {
                        "schema": row["schemaname"],
                        "name": row["tablename"],
                        "approx_rows": row["n_live_tup"],
                        "size_bytes": row["total_bytes"],
                    }
                )

            cursor.close()
            conn.close()

            logger.info("PostgreSQL enumeration completed successfully")
            return result

        except Exception as e:
            logger.error(f"Error enumerating PostgreSQL: {str(e)}")
            return {"error": str(e)}


check_connection = PostgresEnum.check_connection
enumerate = PostgresEnum.enumerate
get_info = PostgresEnum.get_info
