import asyncio
import logging
import os
from src.utils.error_util import ErrorUtil
from src.utils.selenium_util.selenium_util import SeleniumUtil
from src.utils.feed_parser_util import FeedParser
from time import sleep
import pandas as pd
from io import BytesIO
import json
from selenium.common.exceptions import TimeoutException
from src.utils.feed_parser_util import FeedParser

logger = logging.getLogger("Data-scraping")


class GoogleAlertsProcessing:
    def __init__(self):
        self.feed_parser = FeedParser()

    def get_active_option_dropdown_items(
        self, selenium, option_class, available_options
    ):

        # Find all menu items by their role
        menu_items = selenium.wait_for(
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

    def set_option(self, selenium, option_class, user_option, available_options):
        # logger.info("available options:" + str(available_options))
        selenium.click_button("by_class", option_class + "_select")
        logger.info("collecting valid options for " + option_class)
        valid_options2position = self.get_active_option_dropdown_items(
            selenium, option_class, available_options
        )
        logger.info("done collecting valid options")
        sleep(2)  # Brief pause for dropdown animation
        logger.info(
            f"user option and id {user_option}: {valid_options2position[user_option]["id"]}"
        )
        selenium.click_button(
            "by_xpath",
            f"//div[(@id='{valid_options2position[user_option]["id"]}') and @role='menuitem']",
        )
        logger.info("dropdown clicked")
        selenium.press_key(selenium.keys.ESCAPE)
        logger.info("escape button clicked")

    def get_rss_links_list(self, selenium):
        try:
            link_elements = selenium.wait_for(
                "presence_of_all_elements_located",
                "by_css",
                "div.alert_buttons a[href^='/alerts/feeds/']",
                has_special_error_handler=True,
            )
        except TimeoutException as e:
            return "No RSS feed has been found"
        rss_links = set()
        for link_element in link_elements:
            # Extract the href attribute
            rss_feed_path = link_element.get_attribute("href")
            rss_links.add(rss_feed_path)
        logger.info(len(rss_links))
        return rss_links

    def update_rss_db(self, old_df, rss_links):
        new_rss_feed = []
        for rss_link in rss_links:
            rss_element = self.feed_parser.parse_rss(rss_link)
            new_rss_feed.extend(rss_element)
        try:
            already_existing_titles = old_df["Title"].values
        except KeyError:
            already_existing_titles = []
        newly_added_rss_feed = [
            rss_feed
            for rss_feed in new_rss_feed
            if rss_feed["Title"] not in already_existing_titles
        ]
        new_df = pd.DataFrame(newly_added_rss_feed)

        # Concatenate the new data
        return pd.concat([old_df, new_df], ignore_index=True)
