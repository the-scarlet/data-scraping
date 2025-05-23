from src.config import LOG_LEVEL
from src.utils.logger import configure_logging
from .cli_util import cli_util
import asyncio

configure_logging(level=LOG_LEVEL)


async def main():
    cli = cli_util()
    await cli.execute_command()


if __name__ == "__main__":
    asyncio.run(main())
