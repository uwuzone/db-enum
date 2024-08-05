import pymysql
from typing import Dict, Any

from ..db_interface import DBInterface
from ..logger import VerboseLogger


class MySQLEnum(DBInterface):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "name": "MySQL",
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
            conn = pymysql.connect(
                host=host, port=port, user=user, password=password, database=database
            )
            conn.close()
            logger.info(f"Successfully connected to MySQL at {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {str(e)}")
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
            conn = pymysql.connect(
                host=host, port=port, user=user, password=password, database=database
            )
            cursor = conn.cursor()

            result = {
                "type": "MySQL",
                "kind": "sql",
                "version": None,
                "databases": [],
                "tables": [],
            }

            logger.info("Retrieving MySQL version...")
            cursor.execute("SELECT VERSION()")
            result["version"] = cursor.fetchone()[0]

            logger.info("Retrieving database list...")
            cursor.execute("SHOW DATABASES")
            result["databases"] = [row[0] for row in cursor.fetchall()]

            logger.info("Retrieving table information...")
            cursor.execute(
                """
                SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_ROWS, DATA_LENGTH 
                FROM INFORMATION_SCHEMA.TABLES
            """
            )
            for row in cursor.fetchall():
                result["tables"].append(
                    {
                        "schema": row[0],
                        "name": row[1],
                        "approx_rows": row[2],
                        "size_bytes": row[3],
                    }
                )

            cursor.close()
            conn.close()

            logger.info("MySQL enumeration completed successfully")
            return result

        except Exception as e:
            logger.error(f"Error enumerating MySQL: {str(e)}")
            return {"error": str(e)}


check_connection = MySQLEnum.check_connection
enumerate = MySQLEnum.enumerate
get_info = MySQLEnum.get_info
