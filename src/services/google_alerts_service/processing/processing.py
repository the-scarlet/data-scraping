import asyncio
import logging
import os
from src.utils.error_util import ErrorUtil
from src.utils.selenium_util.selenium_util import SeleniumUtil
from src.utils.feed_parser_util import FeedParser
from time import sleep, time
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
        self, selenium, option_class, user_option, available_options
    ):
        try:
            # Find all menu items by their role
            menu_items = selenium.wait_for(
                "presence_of_all_elements_located",
                "by_xpath",
                "//div[@role='menuitem']",
            )

            # Create a list of dictionaries with info about each menu item
            if option_class in available_options.keys():
                logger.info("We laready have the info stocked form last time")
                items_info = available_options[option_class]
                return items_info
            else:
                items_info = dict()
                for item in menu_items:
                    # Get the text content
                    # text = item.text
                    content_div = item.find_element(
                        "xpath", ".//div[@class='goog-menuitem-content']"
                    )
                    text = content_div.text
                    logger.info(text)
                    if text == user_option:
                        # data_value = item.get_attribute("data-value")
                        id = item.get_attribute("id")
                        items_info[text] = {
                            # "data-value": data_value,
                            "id": id
                        }
                        available_options[option_class] = items_info
                        return items_info
                logger.info(
                    f"there is no {option_class} called {user_option}. Try to check that."
                )
                exit(1)
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in get option dropdown items")

    def set_option(self, selenium, option_class, user_option, available_options):
        try:
            t = time()
            selenium.click_button("by_class", option_class + "_select")
            logger.info("collecting valid options for " + option_class)
            valid_options2position = self.get_active_option_dropdown_items(
                selenium, option_class, user_option, available_options
            )
            logger.info("done collecting valid options")
            logger.info(f"Took us {time()-t} s")
            sleep(2)  # Brief pause for dropdown animation
            logger.info(valid_options2position)
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
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in set dropdown option")

    def get_rss_links_list(self, selenium):
        try:
            delivery_settings = selenium.get_elements("by_class", "delivery_settings")
            topics2links = dict()
            for delivery_div in delivery_settings:
                try:
                    # Find the RSS link (the <a> tag containing the RSS icon)
                    rss_link = delivery_div.find_element(
                        "css selector", "a[href*='/alerts/feeds/']"
                    )

                    # Check if it has href (it should, but good to verify)
                    href = rss_link.get_attribute("href")

                    if href:
                        # Get the query text (the span with the search term)
                        query_span = delivery_div.find_element(
                            "css selector", ".query_div span[tabindex='0']"
                        )
                        topic = query_span.text

                        topics2links.setdefault(topic, []).append(href)
                    logger.info("topic: " + str(topic) + " href: " + str(href))
                except Exception as e:
                    logger.info(f"No RSS feed available or error: {e}")
                # Extract the href attribute
            return topics2links
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in get RSS links list")

    def update_rss_db(self, old_df, rss_links):
        try:
            new_rss_feed = []
            for topic in rss_links.keys():
                for rss_link in rss_links[topic]:
                    rss_element = self.feed_parser.parse_rss(rss_link, topic=topic)
                    new_rss_feed.extend(rss_element)
                try:
                    already_existing_titles = old_df["Title"].values
                except KeyError:
                    already_existing_titles = []
                newly_added_rss_feed = []
                for rss_feed in new_rss_feed:
                    if rss_feed["Title"] not in already_existing_titles:
                        newly_added_rss_feed.append(rss_feed)
                    else:
                        break
                new_df = pd.DataFrame(newly_added_rss_feed)

            # Concatenate the new data
            return new_df
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in updating RSS DB")

    def get_active_alerts(self, selenium):
        try:
            alerts = selenium.get_elements("by_css", "li.alert_instance")
            existing_alerts = set()
            for alert in alerts:
                alert_name = alert.find_element(
                    selenium.map_selector("by_css"), ".query_div > span"
                ).text
                existing_alerts.add(alert_name)
            return existing_alerts
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in get active alerts")
