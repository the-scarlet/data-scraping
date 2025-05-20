import asyncio
import logging
import os
from ....config import (
    GOOGLE_COOKIES_FILE,
    ARTEFACTS_DIRECTORY,
    HOME_PATH,
    DEFAULT_ENTRY,
)
from ....utils.error_util import error_util
from ....utils.selenium_util.selenium_util import selenium_util
from ....utils.feed_parser_util import feed_parser
from time import sleep
import pandas as pd
from io import BytesIO
import json

logger = logging.getLogger("Data-scraping")


class google_alerts_preprocessing:
    def google_login(self, driver):
        # Go to the website (login page not needed)
        driver.get("https://www.google.com/alerts")

        # Load saved cookies
        with open(GOOGLE_COOKIES_FILE, "r") as file:
            cookies = json.load(file)

        # Add each cookie to the browser
        for cookie in cookies:
            driver.add_cookie(cookie)

        # Refresh to apply cookies (now logged in)
        driver.refresh()
