import asyncio
import logging
import os
from selenium.common.exceptions import TimeoutException
from ...config import GOOGLE_COOKIES_FILE, ARTEFACTS_DIRECTORY, HOME_PATH, DEFAULT_ENTRY
from ...utils.error_util import error_util
from ...utils.selenium_util.selenium_util import selenium_util
from ...utils.feed_parser_util import feed_parser
from time import sleep
import pandas as pd
from io import BytesIO
import json
from .preprocessing.preprocessing import google_alerts_preprocessing
from .processing.processing import google_alerts_processing

logger = logging.getLogger("Data-scraping")


class google_alerts_service:
    def __init__(self):
        self._selenium = selenium_util()
        self.feed_parser = feed_parser()
        self.preprocessing = google_alerts_preprocessing()
        self.processing = google_alerts_processing()

    def save_session_cookies(self):

        # Go to the login page
        self._selenium.driver.get("https://www.google.com")

        # Manually log in
        # Waiting for you to log in
        try:
            self._selenium.wait_for(
                "element_to_be_clickable",
                "by_xpath",
                "//a[contains(@aria-label, 'Compte Google')]",
                timeout=60,  # seconds before timeout
                has_special_error_handler=True,
            )
        except TimeoutException:
            logger.info("You did not provide credentials! Try to set cookies again!")
            exit(1)
        # # Save cookies to a JSON file
        cookies = self._selenium.driver.get_cookies()
        # create folder
        os.makedirs(os.path.join(HOME_PATH, ARTEFACTS_DIRECTORY), exist_ok=True)
        with open(GOOGLE_COOKIES_FILE, "w") as file:
            json.dump(cookies, file)

        print("Cookies saved successfully!")
        self._selenium.driver.quit()
        return "Success"

    def scrape_google_alerts(self, search_term):
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

    def set_alert(
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
        search_terms = self.preprocessing.commodities(instruments, keywords)
        options = {
            "frequency": frequency,
            "source": source,
            "language": language,
            "region": region,
            "volume": volume,
            "delivery": delivery,
        }
        available_options = dict()
        self.preprocessing.google_login(self._selenium)
        for search_term in search_terms:
            self._selenium.set_text_input_value(
                "by_css", "#query_div input[type='text']", search_term
            )
            self._selenium.click_button("by_css", "span.show_options[role='button']")
            for option in options:
                if options.get(option) != DEFAULT_ENTRY:
                    self.processing.set_option(
                        self._selenium, option, options.get(option), available_options
                    )
            self._selenium.click_button("by_id", "create_alert")
            sleep(2)
        self._selenium.close_driver()
        return f"Request processed successfully. You will get alerts for the terms {search_terms}."

    def get_existing_alerts(self):
        self.preprocessing.google_login(self._selenium)
        self.preprocessing.are_there_google_alerts(self._selenium)
        alerts = self._selenium.get_elements("by_css", "li.alert_instance")
        alert_data = set()
        for alert in alerts:
            alert_name = alert.find_element(
                self._selenium.map_selector("by_css"), ".query_div > span"
            ).text
            alert_data.add(alert_name)
        self._selenium.close_driver()
        return str(alert_data)

    def delete_existing_alerts(self, instruments, keywords):
        self.preprocessing.google_login(self._selenium)
        self.preprocessing.are_there_google_alerts(self._selenium)
        search_terms = self.preprocessing.commodities(instruments, keywords)
        alerts = self._selenium.get_elements("by_css", "li.alert_instance")
        remaining_alerts = set()
        removed_alerts = set()
        for alert in alerts:
            alert_name = alert.find_element(
                self._selenium.map_selector("by_css"), ".query_div > span"
            ).text
            if alert_name in search_terms:
                delete_button = alert.find_element(
                    self._selenium.map_selector("by_css"), ".delete_button.alert_button"
                )
                delete_button.click()
                removed_alerts.add(alert_name)
            else:
                remaining_alerts.add(alert_name)
        self._selenium.close_driver()
        return f"Removed Alerts: {removed_alerts}\nRemaining Alerts: {remaining_alerts}"

    def get_rss_news(self):
        self.preprocessing.google_login(self._selenium)
        self.preprocessing.are_there_google_alerts(self._selenium)
        rss_links = self.processing.get_rss_links_list(self._selenium)
        self._selenium.close_driver()
        rss_feed = []
        for rss_link in rss_links:
            rss_element = self.feed_parser.parse_rss(rss_link)
            rss_feed.extend(rss_element)
        return rss_feed
