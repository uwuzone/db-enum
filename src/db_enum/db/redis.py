import redis
from typing import Dict, Any
from ..db_interface import DBInterface
from ..logger import VerboseLogger


class RedisEnum(DBInterface):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "name": "Redis",
            "kind": "key-value",
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
            r = redis.Redis(
                host=host,
                port=port,
                username=user,
                password=password,
                db=int(database or 0),
            )
            r.ping()
            logger.info(f"Successfully connected to Redis at {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
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
        r = redis.Redis(
            host=host,
            port=port,
            username=user,
            password=password,
            db=int(database or 0),
        )

        result = {
            "type": "Redis",
            "kind": "key-value",
            "version": None,
            "databases": [],
            "key_stats": [],
        }

        logger.info("Retrieving Redis version...")
        info = r.info()
        result["version"] = info.get("redis_version")

        logger.info("Retrieving database information...")
        for i in range(16):  # Redis typically has 16 databases by default
            r.select(i)
            db_size = r.dbsize()
            if db_size > 0:
                result["databases"].append(f"db{i}")
                result["key_stats"].append(
                    {
                        "database": f"db{i}",
                        "key_count": db_size,
                        "memory_used": r.info(section="memory").get(
                            "used_memory_human"
                        ),
                    }
                )

        logger.info("Redis enumeration completed successfully")
        return result


check_connection = RedisEnum.check_connection
enumerate = RedisEnum.enumerate
get_info = RedisEnum.get_info
