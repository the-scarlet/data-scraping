import logging


def configure_logging(level: str = "INFO"):
    logging.basicConfig(
        level=level.upper(),  # Use the provided log level
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger("Data-scraping")
