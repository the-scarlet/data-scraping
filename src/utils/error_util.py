import logging

logger = logging.getLogger("Data-scraping")


class error_util:
    @staticmethod
    def handle_error(error, status):
        logger.error(f"{status} error: {error}")
        exit(1)
