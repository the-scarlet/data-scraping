import logging

logger = logging.getLogger("Data-scraping")


class ErrorUtil:
    @staticmethod
    def handle_error(error, status):
        logger.error(f"{status} error: {error}")
        exit(1)
