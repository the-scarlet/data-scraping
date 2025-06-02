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
from datetime import datetime, timedelta
import json
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.utils.dynamic_paths_util import DynamicPaths

logger = logging.getLogger("Data-scraping")
config = AppConfig()


class GoogleAlertsPreprocessing:
    async def google_login(self, playwright):
        try:
            # Go to the website (login page not needed)
            await playwright.get_url("https://www.google.com/alerts")

            # Load saved cookies
            try:
                with open(config.cookies_path, "r") as file:
                    cookies = json.load(file)
            except:
                logger.info(
                    "There was a problem loading your cookies, try to set them again (command: set-cookies)"
                )
                exit(1)

            # Add cookies to the browser
            await playwright.context.add_cookies(cookies)

            # Refresh to apply cookies (now logged in)
            await playwright.page.reload()

            # Make sure you are logged in
            try:
                await playwright.wait_for(
                    "by_xpath",
                    "//a[contains(@aria-label, 'Compte Google')]",
                    has_special_error_handler=True,
                )
            except ValueError:
                await playwright.close_driver()
                logger.info(
                    "Did not manage to log in, Maybe you need to reset your cookies (command: set-cookies)"
                )
                exit(1)
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in google login")

    async def are_there_google_alerts(self, playwright):

        alerts = await playwright.page.locator(
            "div#manage-alerts-div li.alert_instance"
        ).all()
        logger.info("alerts found: " + str(len(alerts)))
        if len(alerts) == 0:
            await playwright.close_driver()
            logger.info("No Active Alerts Have Been Found")
            exit(0)

    def are_there_rss_alerts(self, selenium):
        try:
            self.are_there_google_alerts(selenium)
            # Locate the delivery settings div
            delivery_settings = selenium.get_elements("by_class", "delivery_settings")
            # logger.info(len(delivery_settings))
            logger.info(
                "delivery html: " + str(delivery_settings[5].get_attribute("outerHTML"))
            )
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
        except Exception as e:
            return ErrorUtil.handle_error(
                e, "Error while testing if there are RSS alerts"
            )

    def commodities(self, instruments, keywords):
        try:
            commodities_list = []
            if keywords == []:
                keywords = [""]
            for instrument in instruments:
                for keyword in keywords:
                    commodities_list.append(instrument + " " + keyword)
            return commodities_list
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in creating commodities")

    def last_rss(self):  # returns pandas
        topics = os.listdir(config.google_alerts_output_path)
        if topics == []:
            logger.info("there are No topics yet")
            return pd.DataFrame([])
        logger.info(topics)
        rows_list = []
        for topic in topics:
            full_path = DynamicPaths().most_recent_path(
                os.path.join(config.google_alerts_output_path, topic)
            )
            if str(full_path) == str(DynamicPaths().path(topic[topic.find("=") + 1 :])):
                logger.info(
                    "Last time RSS feed was collected for {topic} is today, try again tomorrow"
                )
                continue
            logger.info(f"here is the most recent path for {topic}: {full_path}")
            try:
                old_news = pd.read_excel(os.path.join(full_path, "google_alerts.xlsx"))
                first_row = old_news.head(1)
                rows_list.append(first_row)
                logger.info("added new element!")
            except Exception as e:
                logger.info(f"there is a problem {e}")
        logger.info("first rows")
        logger.info(rows_list)
        return (
            pd.concat(rows_list, ignore_index=True) if rows_list else pd.DataFrame([])
        )
