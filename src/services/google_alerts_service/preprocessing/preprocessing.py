import asyncio
import logging
import os
from config.config import AppConfig
from src.utils.error_util import ErrorUtil
from src.utils.selenium_util.selenium_util import SeleniumUtil
from src.utils.feed_parser_util import FeedParser
from time import sleep
import pandas as pd
from io import BytesIO
import json
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger("Data-scraping")
config = AppConfig()


class GoogleAlertsPreprocessing:
    def google_login(self, selenium):
        # Go to the website (login page not needed)
        selenium.driver.get("https://www.google.com/alerts")

        # Load saved cookies
        try:
            with open(config.cookies_path, "r") as file:
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
            return "No Active Alerts Have Been Found"

    def are_there_rss_alerts(self, selenium):
        self.are_there_google_alerts(selenium)
        # Locate the delivery settings div
        delivery_settings = selenium.get_elements("by_class", "delivery_settings")
        logger.info(len(delivery_settings))
        logger.info(delivery_settings[0].get_attribute("outerHTML"))
        # Find the RSS icon within the alert buttons section
        for delivery_setting in delivery_settings:
            try:
                rss_icon = delivery_setting.find_element(
                    "css selector", ".alert_buttons .rss_icon"
                )
                return
            except NoSuchElementException:
                pass
        logger.info("No RSS Feed has been found")
        exit(1)

    def commodities(self, instruments, keywords):
        commodities_list = []
        if keywords == []:
            keywords = [""]
        for instrument in instruments:
            for keyword in keywords:
                commodities_list.append(instrument + " " + keyword)
        return commodities_list
