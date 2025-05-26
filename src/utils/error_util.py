import logging

logger = logging.getLogger("Data-scraping")


class ErrorUtil:
    @staticmethod
    def handle_error(error, context: str):
        logger.error(f"{context}: {error}")
        exit(1)
