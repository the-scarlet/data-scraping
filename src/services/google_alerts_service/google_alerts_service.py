import asyncio
import logging
import os

# Or for synchronous Playwright:
# from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from config.config import AppConfig
from src.utils.error_util import ErrorUtil
from src.utils.selenium_util.selenium_util import SeleniumUtil
from src.utils.feed_parser_util import FeedParser
from time import sleep
import pandas as pd
from io import BytesIO
import json
from tqdm import tqdm
from src.services.google_alerts_service.preprocessing.preprocessing import (
    GoogleAlertsPreprocessing,
)
from src.services.google_alerts_service.processing.processing import (
    GoogleAlertsProcessing,
)
from src.utils.playwright_util.playwright_util import PlaywrightUtil

logger = logging.getLogger("Data-scraping")
config = AppConfig()


class GoogleAlertsService:

    def __init__(self):
        # Initialize synchronous components
        self._selenium = SeleniumUtil()
        self.preprocessing = GoogleAlertsPreprocessing()
        self.processing = GoogleAlertsProcessing()
        self.playwright = None  # Will be set in async init

    @classmethod
    async def create(cls):
        """Async factory method to properly initialize the class."""
        instance = cls()  # Calls __init__ synchronously
        instance.playwright = await PlaywrightUtil.create()  # Async setup
        return instance

    async def save_session_cookies(self):
        logger.info("starting cookies")
        # try:
        # Go to the login page
        # self._selenium.driver.get("https://www.google.com")
        await self.playwright.get_url("https://www.google.com")
        # Manually log in
        # Waiting for you to log in
        # sleep(3)
        try:
            await self.playwright.wait_for(
                "by_xpath",
                "//a[contains(@aria-label, 'Compte Google')]",
                timeout=60000,  # seconds before timeout
                has_special_error_handler=True,
            )
        except Exception as e:
            logger.info("You did not provide credentials! Try to set cookies again!")
            # logger.info(e)
            await self.playwright.close_driver()
            exit(1)
        # # Save cookies to a JSON file
        cookies = await self.playwright.context.cookies()
        # create folder
        with open(config.cookies_path, "w") as file:
            json.dump(cookies, file)

        print("Cookies saved successfully!")
        # self._selenium.driver.quit()
        await self.playwright.close_driver()
        return "Success"

    # except Exception as e:
    #     return ErrorUtil.handle_error(e, "Error in save cookies")

    def scrape_google_alerts(self, search_term):
        # try:
        # scrapes an alert, no login required
        self._selenium.get_url("https://www.google.com/alerts")

        self._selenium.set_text_input_value(
            "by_css", "#query_div input[type='text']", search_term
        )
        self._selenium.wait_for("element_to_be_clickable", "by_id", "create_alert")
        scraped_data = self._selenium.get_elements("by_css", "a.result_title_link")
        titles = []
        urls = []
        for link in scraped_data:
            url = link.get_attribute("href")  # Get href attribute
            title = link.text  # Get visible text
            if url and title:  # Skip empty entries
                urls.append(url)
                titles.append(title)
        self._selenium.close_driver()
        # Create a DataFrame
        df = pd.DataFrame({"Title": titles, "URL": urls})

        # Export to Excel in memory
        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        output.seek(0)

    # except Exception as e:
    #     return ErrorUtil.handle_error(e, "Error in scrape alerts")

    async def set_alert(
        self,
        instruments,
        keywords,
        frequency,
        source,
        language,
        region,
        volume,
        delivery,
    ):
        # try:
        search_terms = set(self.preprocessing.commodities(instruments, keywords))
        options = {
            "frequency": frequency,
            "source": source,
            "language": language,
            "region": region,
            "volume": volume,
            "delivery": delivery,
        }
        available_options = dict()
        await self.preprocessing.google_login(self.playwright)
        logger.info("logged in")
        sleep(3)
        existing_alerts = await self.processing.get_active_alerts(self.playwright)
        logger.info(f"You already have these active alerts:{existing_alerts}")

        for search_term in tqdm(search_terms - existing_alerts, desc="Processing"):

            await self.playwright.set_text_input_value(
                "by_css",
                "#query_div input[type='text']",
                search_term,
            )

            await self.playwright.click_button(
                "by_css", "span.show_options[role='button']"
            )
            if not available_options:
                available_options = (
                    await self.processing.get_active_option_dropdown_items(
                        self.playwright
                    )
                )
            for option in options:
                if options.get(option) != config.default_entry:
                    await self.processing.set_option(
                        self.playwright,
                        option,
                        options.get(option),
                        available_options,
                    )
            await self.playwright.click_button("by_id", "#create_alert")
            sleep(2)
        await self.playwright.close_driver()
        return search_terms

    # except Exception as e:
    #     return ErrorUtil.handle_error(e, "Error in set alert service")

    async def get_existing_alerts(self):
        # try:
        await self.preprocessing.google_login(self.playwright)
        await self.preprocessing.are_there_google_alerts(self.playwright)
        existing_alerts = await self.processing.get_active_alerts(self.playwright)
        await self.playwright.close_driver()
        return existing_alerts

    # except Exception as e:
    #     ErrorUtil.handle_error(e, "Error in get existing alerts service")

    async def delete_existing_alerts(self, instruments, keywords):
        # try:
        await self.preprocessing.google_login(self.playwright)
        await self.preprocessing.are_there_google_alerts(self.playwright)
        search_terms = self.preprocessing.commodities(instruments, keywords)
        alerts = await self.playwright.page.locator(
            "div#manage-alerts-div li.alert_instance"
        ).all()
        logger.info("alert: " + str(alerts[0]))
        remaining_alerts = set()
        removed_alerts = set()
        for alert in alerts:
            alert_name = await alert.locator(".query_div > span").inner_text()
            if alert_name in search_terms:
                delete_button = alert.locator(".delete_button")
                await delete_button.click()
                removed_alerts.add(alert_name)
            else:
                remaining_alerts.add(alert_name)
        await self.playwright.close_driver()
        return {
            "Removed Alerts": removed_alerts,
            "Remaining Alerts": remaining_alerts,
        }

    # except Exception as e:
    #     return ErrorUtil.handle_error(e, "Error in delete alerts")

    async def get_rss_news(self):
        # try:
        old_news = self.preprocessing.last_rss()
        # pd.read_excel(
        #     config.excel_path
        # )  # pd.read_parquet(config.parquet_path, engine='pyarrow')
        logger.info("old news: ")
        logger.info(old_news)
        await self.preprocessing.google_login(self.playwright)
        await self.preprocessing.are_there_google_alerts(self.playwright)
        rss_links = await self.processing.get_rss_links_list(self.playwright)
        await self.playwright.close_driver()
        rss_feed = self.processing.update_rss_db(old_news, rss_links)
        return rss_feed

    # except Exception as e:
    #     return ErrorUtil.handle_error(e, "Error in get RSS news service")
