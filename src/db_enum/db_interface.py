from abc import ABC, abstractmethod
from typing import Dict, Any

from .logger import VerboseLogger


class DBInterface(ABC):
    @staticmethod
    @abstractmethod
    def get_info() -> Dict[str, Any]:
        pass

    @staticmethod
    @abstractmethod
    def check_connection(
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        logger: VerboseLogger,
    ) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def enumerate(
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        logger: VerboseLogger,
    ) -> Dict[str, Any]:
        pass
