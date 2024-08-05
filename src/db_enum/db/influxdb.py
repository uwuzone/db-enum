from influxdb import InfluxDBClient
from typing import Dict, Any
from ..db_interface import DBInterface
from ..logger import VerboseLogger


class InfluxDBEnum(DBInterface):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "name": "InfluxDB",
            "kind": "time-series",
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
            client = InfluxDBClient(
                host=host,
                port=port,
                username=user,
                password=password,
                database=database,
            )
            client.ping()
            logger.info(f"Successfully connected to InfluxDB at {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {str(e)}")
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
        client = InfluxDBClient(
            host=host,
            port=port,
            username=user,
            password=password,
            database=database,
        )

        result = {
            "type": "InfluxDB",
            "kind": "time-series",
            "version": None,
            "databases": [],
            "measurements": [],
        }

        logger.info("Retrieving InfluxDB version...")
        version = client.request("ping", expected_response_code=204).headers.get(
            "X-Influxdb-Version"
        )
        result["version"] = version

        logger.info("Retrieving database list...")
        result["databases"] = client.get_list_database()

        logger.info("Retrieving measurements for each database...")
        for db in result["databases"]:
            client.switch_database(db["name"])
            measurements = client.get_list_measurements()
            for measurement in measurements:
                result["measurements"].append(
                    {"database": db["name"], "name": measurement["name"]}
                )

        logger.info("InfluxDB enumeration completed successfully")
        return result


check_connection = InfluxDBEnum.check_connection
enumerate = InfluxDBEnum.enumerate
get_info = InfluxDBEnum.get_info
