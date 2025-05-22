from config.config import AppConfig
from src.utils.logger import configure_logging
from cli.cli_util import CliUtil
import asyncio

config = AppConfig()
configure_logging(level=config.log_level)


async def main():
    cli = CliUtil()
    await cli.execute_command()


if __name__ == "__main__":
    asyncio.run(main())
