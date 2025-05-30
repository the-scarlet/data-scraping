from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from src.utils.error_util import ErrorUtil
from config.selenium_config import SeleniumConfig
from src.utils.error_util import ErrorUtil

import asyncio
from playwright.async_api import async_playwright

selenium_config = SeleniumConfig()


class PlaywrightUtil:
    def __init__(self):
        pass

    @classmethod
    async def create(cls):
        """Async factory method to properly initialize the class."""
        instance = cls()  # Calls __init__ synchronously
        # with async_playwright() as p:
        p = await async_playwright().start()
        instance.playwright = p
        # Browser launch arguments (equivalent to chrome_options.add_argument)
        instance.browser = await p.chromium.launch(
            # # Equivalent to chrome_options.binary_location
            # executable_path="/path/to/chrome/binary",  # Set your chrome binary path here
            headless=False,  # Set to True for headless mode
            args=[
                # Important flags to prevent login prompts
                "--disable-popup-blocking",
                "--disable-notifications",
                "--no-first-run",
                "--no-default-browser-check",
                "--password-store=basic",
                "--disable-sync",
                # Crucial additions
                "--guest",  # Run in guest mode (no profiles)
                "--incognito",  # Run in incognito mode
                "--disable-extensions",  # Disable all extensions
                "--disable-blink-features=AutomationControlled",
                # Hide automation (equivalent to excludeSwitches and useAutomationExtension)
                # "--disable-web-security",
                # "--disable-features=VizDisplayCompositor",
                # Language setting
                f"--lang={selenium_config.chromium_country_language}",  # Replace with your language code
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        # Create context with additional options
        context = await instance.browser.new_context(
            # Language and locale settings
            locale=selenium_config.chromium_country_language,  # e.g., 'en-US', 'fr-FR'
            # Additional privacy/stealth settings
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Disable geolocation, notifications etc.
            permissions=[],  # Empty permissions list
            # Extra HTTP headers to hide automation
            extra_http_headers={
                "Accept-Language": f"{selenium_config.chromium_country_language},en;q=0.9",
            },
        )

        # Remove automation indicators (equivalent to experimental options)
        await context.add_init_script(
            """
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Remove automation indicators
            delete window.navigator.__proto__.webdriver;
            
            // Override plugins length
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            
            });
        """
        )
        #  // Override languages
        #     Object.defineProperty(navigator, 'languages', {
        #         get: () => ['en-US', 'en'],

        instance.context = context
        instance.page = await context.new_page()
        return instance

    async def get_url(self, url):
        await self.page.goto(url)

    def map_selenium_condition(self, condition):
        try:
            return selenium_config.expected_conditions[condition]
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in map selenium condition")

    def wait_for(
        self,
        wait_condition,
        selection_method,
        locator,
        timeout=selenium_config.timeout,
        has_special_error_handler=False,
    ):
        return
        # try:

        #     # condition = self.map_selenium_condition(wait_condition)
        #     if has_special_error_handler:
        #         element = WebDriverWait(self.driver, timeout).until(
        #             condition((selector, locator))
        #         )
        #     else:
        #         try:
        #             element = WebDriverWait(self.driver, timeout).until(
        #                 condition((selector, locator))
        #             )
        #         except TimeoutException as e:
        #             ErrorUtil.handle_error(
        #                 e,
        #                 "This exception is the result of not finding an element in the page.",
        #             )
        #             exit(1)
        #     return element
        # except Exception as e:
        #     return ErrorUtil.handle_error(e, "Error in wait for")

    def set_text_input_value(
        self, selection_method, locator, text, timeout=selenium_config.timeout
    ):
        try:
            # text_input = self.wait_for(
            #     "element_to_be_clickable", selection_method, locator, timeout
            # )
            text_input = self.page.locator(locator)
            text_input.send_keys(text)
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in set selenium text")

    def click_button(self, selection_method, locator, timeout=selenium_config.timeout):
        try:
            self.page.click(locator)
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in click selenium button")

    async def get_elements(
        self, selection_method, locator, timeout=selenium_config.timeout
    ):
        try:
            # selector = self.map_selector(selection_method)
            # self.wait_for(
            #     "presence_of_all_elements_located", selection_method, locator, timeout
            # )
            elements = await self.page.locator(locator).wait_for(
                state="visible", timeout=timeout
            )
            return elements
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in get selenium elements")

    async def close_driver(self):
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()

    def press_key(self, locator, key):
        self.page.locator(locator).press(key)
