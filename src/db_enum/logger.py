import logging


class VerboseLogger:
    def __init__(self, verbose: bool):
        self.verbose = verbose
        if verbose:
            logging.basicConfig(level=logging.INFO, format="%(message)s")
        self.logger = logging.getLogger(__name__)

    def info(self, message: str):
        if self.verbose:
            self.logger.info(message)

    def error(self, message: str):
        if self.verbose:
            self.logger.error(message)
