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

    async def get_active_option_dropdown_items(self, playwright):
        # try:
        # Find all menu items by their role
        # menu_items = await playwright.page.query_selector_all(".goog-menuitem")
        # items_info = dict()
        # for item in menu_items:
        #     selector = await item.query_selector(".goog-menuitem-content")
        #     content = await selector.inner_text()
        #     item_id = await item.get_attribute("id")
        #     print(f"ID: {item_id}, Text: {content}")
        #     if content not in items_info.keys():

        #         items_info[content] = item_id
        items_info = {
            "Quand le cas se présente": ":0",
            "Automatique": ":7",
            "Finance": ":f",
            "Toutes les langues": ":h",
            "Toutes les régions": ":1u",
            "Seulement les meilleurs résultats": ":4",
            "Tous les résultats": ":5",
            "Flux RSS": ":8l",
        }

        return items_info

    # except Exception as e:
    #     return ErrorUtil.handle_error(e, "Error in get option dropdown items")

    async def set_option(
        self, playwritght, option_class, user_option, available_options
    ):
        # try:
        t = time()

        logger.info("collecting valid options for " + option_class)
        valid_options2position = available_options
        if option_class == "delivery":
            dropdown_locator = "div.delivery_select div.goog-flat-menu-button"
            option_locator = f"div.goog-menu.goog-menu-vertical div#\\{valid_options2position[user_option]}"
        else:
            dropdown_locator = f"div.goog-flat-menu-button.{option_class}_select"
            option_locator = f"div.goog-menu.goog-menu-noicon div#\\{valid_options2position[user_option]}"
        logger.info(f"dropdown : {dropdown_locator}, option: {option_locator}")
        logger.info("done collecting valid options")
        sleep(1)
        await playwritght.click_button(
            "by_class",
            dropdown_locator,
        )
        logger.info(f"Took us {time()-t} s")
        sleep(1)  # Brief pause for dropdown animation
        await playwritght.page.click(option_locator)

        sleep(1)
        await playwritght.press_key(option_locator, "Escape")

    async def get_rss_links_list(self, playwright):
        # try:
        delivery_settings = await playwright.page.locator(".delivery_settings").all()
        logger.info("delivery setting: " + str(delivery_settings[0]))
        topics2links = dict()
        topic = ""
        for delivery_div in delivery_settings:
            logger.info("aaaaa")
            # try:
            # Find the RSS link (the <a> tag containing the RSS icon)
            rss_anchor = delivery_div.locator("a:has(span.rss_icon)")
            if await rss_anchor.count() > 0:
                href = "https://www.google.fr" + await rss_anchor.get_attribute("href")
            else:
                href = ""

            if href:
                # Get the query text (the span with the search term)
                topic_locator = delivery_div.locator(".query_div span[tabindex='0']")
                topic = (
                    await topic_locator.inner_text()
                    if await topic_locator.count() > 0
                    else None
                )

                topics2links.setdefault(topic, []).append(href)
            logger.info("topic: " + str(topic) + " href: " + str(href))
        logger.info(topics2links)
        # except Exception as e:
        #     logger.info(f"No RSS feed available or error: {e}")
        # Extract the href attribute
        return topics2links

    # except Exception as e:
    #     return ErrorUtil.handle_error(e, "Error in get RSS links list")

    def update_rss_db(self, old_df, rss_links):
        try:
            new_rss_feed = []
            for topic in rss_links.keys():
                logger.info(topic)
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
            logger.info(new_df)
            return new_df

        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in updating RSS DB")

    async def get_active_alerts(self, playwright):
        # try:
        logger.info("getting active alerts")
        titles = await playwright.page.locator(
            "li.alert_instance .query_div > span"
        ).all_inner_texts()

        return titles

    # except Exception as e:
    #     return ErrorUtil.handle_error(e, "Error in get active alerts")
