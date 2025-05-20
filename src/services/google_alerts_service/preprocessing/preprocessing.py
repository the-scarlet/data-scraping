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
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger("Data-scraping")


class google_alerts_preprocessing:
    def google_login(self, selenium):
        # Go to the website (login page not needed)
        selenium.driver.get("https://www.google.com/alerts")

        # Load saved cookies
        try:
            with open(GOOGLE_COOKIES_FILE, "r") as file:
                cookies = json.load(file)
        except:
            logger.info(
                "There was a problem loading your cookies, try to set them again (command: set-cookies)"
            )
            exit(1)

        # Add each cookie to the browser
        for cookie in cookies:
            selenium.driver.add_cookie(cookie)

        # Refresh to apply cookies (now logged in)
        selenium.driver.refresh()

        # Make sure you are logged in
        try:
            selenium.wait_for(
                "element_to_be_clickable",
                "by_xpath",
                "//a[contains(@aria-label, 'Compte Google')]",
                has_special_error_handler=True,
            )
        except TimeoutException:
            selenium.close_driver()
            logger.info(
                "Did not manage to log in, Maybe you need to reset your cookies (command: set-cookies)"
            )
            exit(1)

    def are_there_google_alerts(self, selenium):
        try:
            selenium.wait_for(
                "element_to_be_clickable",
                "by_id",
                "manage-alerts-div",
                has_special_error_handler=True,
            )
        except TimeoutException:
            selenium.close_driver()
            logger.info("No Active Alerts Have Been Found")
            exit(0)

    def commodities(self, instruments, keywords):
        commodities_list = []
        if keywords == []:
            keywords = [""]
        for instrument in instruments:
            for keyword in keywords:
                commodities_list.append(instrument + " " + keyword)
        return commodities_list
