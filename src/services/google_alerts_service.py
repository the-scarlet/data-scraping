import asyncio
import logging
import os
from selenium.common.exceptions import TimeoutException
from ..config import GOOGLE_COOKIES_FILE, ARTEFACTS_DIRECTORY, HOME_PATH, DEFAULT_ENTRY
from ..utils.error_util import error_util
from ..utils.selenium_util.selenium_util import selenium_util
from ..utils.feed_parser_util import feed_parser
from time import sleep
import pandas as pd
from io import BytesIO
import json

logger = logging.getLogger("Data-scraping")


class google_alerts_service:
    def __init__(self):
        self._selenium = selenium_util()
        self.feed_parser = feed_parser()

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

    def google_login(self):
        # Go to the website (login page not needed)
        self._selenium.driver.get("https://www.google.com/alerts")

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
            self._selenium.driver.add_cookie(cookie)

        # Refresh to apply cookies (now logged in)
        self._selenium.driver.refresh()

        # Make sure you are logged in
        try:
            self._selenium.wait_for(
                "element_to_be_clickable",
                "by_xpath",
                "//a[contains(@aria-label, 'Compte Google')]",
                has_special_error_handler=True,
            )
        except TimeoutException:
            self._selenium.close_driver()
            logger.info(
                "Did not manage to log in, Maybe you need to reset your cookies (command: set-cookies)"
            )
            exit(1)

    def are_there_google_alerts(self):
        try:
            self._selenium.wait_for(
                "element_to_be_clickable",
                "by_id",
                "manage-alerts-div",
                has_special_error_handler=True,
            )
        except TimeoutException:
            self._selenium.close_driver()
            logger.info("No Active Alerts Have Been Found")
            exit(0)

    def get_active_option_dropdown_items(self, option_class, available_options):

        # Find all menu items by their role
        menu_items = self._selenium.wait_for(
            "presence_of_all_elements_located", "by_xpath", "//div[@role='menuitem']"
        )

        # Create a list of dictionaries with info about each menu item
        if option_class in available_options.keys():
            items_info = available_options[option_class]
        else:
            items_info = dict()
            for item in menu_items:
                # Get the text content
                # text = item.text
                content_div = item.find_element(
                    "xpath", ".//div[@class='goog-menuitem-content']"
                )
                text = content_div.text
                data_value = item.get_attribute("data-value")
                id = item.get_attribute("id")
                # logger.info(text + str(data_value))
                if text:
                    items_info[text] = {"data-value": data_value, "id": id}
            available_options[option_class] = items_info
        return items_info

    def set_option(self, option_class, user_option, available_options):
        # logger.info("available options:" + str(available_options))
        self._selenium.click_button("by_class", option_class + "_select")
        logger.info("collecting valid options for " + option_class)
        valid_options2position = self.get_active_option_dropdown_items(
            option_class, available_options
        )
        logger.info("done collecting valid options")
        sleep(1)  # Brief pause for dropdown animation
        logger.info(
            f"user option and id {user_option}: {valid_options2position[user_option]["id"]}"
        )
        self._selenium.click_button(
            "by_xpath",
            f"//div[(@id='{valid_options2position[user_option]["id"]}') and @role='menuitem']",
        )
        logger.info("dropdown clicked")
        self._selenium.press_key(self._selenium.keys.ESCAPE)
        logger.info("escape button clicked")

    def commodities(self, instruments, keywords):
        commodities_list = []
        if keywords == []:
            keywords = [""]
        for instrument in instruments:
            for keyword in keywords:
                commodities_list.append(instrument + " " + keyword)

        return commodities_list

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
        search_terms = self.commodities(instruments, keywords)
        options = {
            "frequency": frequency,
            "source": source,
            "language": language,
            "region": region,
            "volume": volume,
            "delivery": delivery,
        }
        available_options = dict()
        self._selenium.get_url("https://www.google.com/alerts")
        self.google_login()
        for search_term in search_terms:
            self._selenium.set_text_input_value(
                "by_css", "#query_div input[type='text']", search_term
            )
            self._selenium.click_button("by_css", "span.show_options[role='button']")
            for option in options:
                if options.get(option) != DEFAULT_ENTRY:
                    self.set_option(option, options.get(option), available_options)

            self._selenium.click_button("by_id", "create_alert")
            sleep(2)
        self._selenium.close_driver()
        return f"Request processed successfully. You will get alerts for the terms {search_terms}."

    def get_existing_alerts(self):

        self._selenium.get_url("https://www.google.com/alerts")
        self.google_login()
        self.are_there_google_alerts()
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
        self._selenium.get_url("https://www.google.com/alerts")
        self.google_login()
        self.are_there_google_alerts()
        search_terms = self.commodities(instruments, keywords)
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
        return (
            f"Removed Alerts: {removed_alerts}\n Remaining Alerts: {remaining_alerts}"
        )

    def get_rss_links_list(self):
        try:
            link_elements = self._selenium.wait_for(
                "presence_of_all_elements_located",
                "by_css",
                "div.alert_buttons a[href^='/alerts/feeds/']",
                has_special_error_handler=True,
            )
        except TimeoutException as e:
            return "No RSS feed has been found"
        logger.info("link elements" + str(link_elements))
        rss_links = set()
        for link_element in link_elements:
            # Extract the href attribute
            rss_feed_path = link_element.get_attribute("href")
            rss_links.add(rss_feed_path)
        logger.info(len(rss_links))
        return rss_links

    def get_rss_news(self):

        self._selenium.get_url("https://www.google.com/alerts")
        self.google_login()
        self.are_there_google_alerts()
        rss_links = self.get_rss_links_list()
        self._selenium.close_driver()
        rss_feed = []
        for rss_link in rss_links:
            rss_element = self.feed_parser.parse_rss(rss_link)
            rss_feed.extend(rss_element)

        return rss_feed
