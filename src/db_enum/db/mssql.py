import pymssql
from typing import Dict, Any
from ..db_interface import DBInterface
from ..logger import VerboseLogger


class MSSQLEnum(DBInterface):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "name": "Microsoft SQL Server",
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
            conn = pymssql.connect(
                server=host, port=port, user=user, password=password, database=database
            )
            conn.close()
            logger.info(f"Successfully connected to MSSQL at {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MSSQL: {str(e)}")
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
        conn = pymssql.connect(
            server=host, port=port, user=user, password=password, database=database
        )
        cursor = conn.cursor(as_dict=True)

        result = {
            "type": "Microsoft SQL Server",
            "kind": "sql",
            "version": None,
            "databases": [],
            "tables": [],
        }

        logger.info("Retrieving MSSQL version...")
        cursor.execute("SELECT @@VERSION")
        result["version"] = cursor.fetchone()[""]

        logger.info("Retrieving database list...")
        cursor.execute("SELECT name FROM sys.databases")
        result["databases"] = [row["name"] for row in cursor.fetchall()]

        logger.info("Retrieving table information...")
        cursor.execute(
            """
            SELECT 
                s.name AS schema_name,
                t.name AS table_name,
                p.rows AS row_count,
                SUM(a.total_pages) * 8 * 1024 AS total_space_bytes
            FROM 
                sys.tables t
                INNER JOIN sys.indexes i ON t.object_id = i.object_id
                INNER JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
                INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
                LEFT JOIN sys.schemas s ON t.schema_id = s.schema_id
            GROUP BY 
                t.name, s.name, p.rows
        """
        )
        for row in cursor.fetchall():
            result["tables"].append(
                {
                    "schema": row["schema_name"],
                    "name": row["table_name"],
                    "approx_rows": row["row_count"],
                    "size_bytes": row["total_space_bytes"],
                }
            )

        cursor.close()
        conn.close()

        logger.info("MSSQL enumeration completed successfully")
        return result


check_connection = MSSQLEnum.check_connection
enumerate = MSSQLEnum.enumerate
get_info = MSSQLEnum.get_info
