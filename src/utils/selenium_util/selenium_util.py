from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from src.utils.error_util import ErrorUtil
from config.selenium_config import SeleniumConfig
from src.utils.error_util import ErrorUtil

selenium_config = SeleniumConfig()


class SeleniumUtil:
    def __init__(self):
        # Set path to your Chrome binary
        chrome_options = Options()
        chrome_options.binary_location = selenium_config.chrome_binary_location

        # Important flags to prevent login prompts
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--password-store=basic")
        chrome_options.add_argument("--disable-sync")

        # These are crucial additions:
        chrome_options.add_argument("--guest")  # Run in guest mode (no profiles)
        chrome_options.add_argument("--incognito")  # Run in incognito mode
        chrome_options.add_argument("--disable-extensions")  # Disable all extensions
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # Hide automation
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # Set language preferences
        chrome_options.add_argument(
            f"--lang={selenium_config.chromium_country_language}"
        )

        # If needed, use a completely temporary profile
        # chrome_options.add_argument("--user-data-dir=./temp_profile")

        # Initialize WebDriver with options
        self.driver = webdriver.Chrome(options=chrome_options)

        # to type sth using keyboard
        self.keys = Keys

    def get_url(self, url):
        self.driver.get(url)

    def map_selector(self, selection_method):
        try:
            return selenium_config.selectors[selection_method]
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in map selenium selector")

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
        try:
            selector = self.map_selector(selection_method)
            condition = self.map_selenium_condition(wait_condition)
            if has_special_error_handler:
                element = WebDriverWait(self.driver, timeout).until(
                    condition((selector, locator))
                )
            else:
                try:
                    element = WebDriverWait(self.driver, timeout).until(
                        condition((selector, locator))
                    )
                except TimeoutException as e:
                    ErrorUtil.handle_error(
                        e,
                        "This exception is the result of not finding an element in the page.",
                    )
                    exit(1)
            return element
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in wait for")

    def set_text_input_value(
        self, selection_method, locator, text, timeout=selenium_config.timeout
    ):
        try:
            text_input = self.wait_for(
                "element_to_be_clickable", selection_method, locator, timeout
            )
            text_input.send_keys(text)
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in set selenium text")

    def click_button(self, selection_method, locator, timeout=selenium_config.timeout):
        try:
            button = self.wait_for(
                "element_to_be_clickable", selection_method, locator, timeout
            )
            button.click()
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in click selenium button")

    def get_elements(self, selection_method, locator, timeout=selenium_config.timeout):
        try:
            selector = self.map_selector(selection_method)
            self.wait_for(
                "presence_of_all_elements_located", selection_method, locator, timeout
            )
            elements = self.driver.find_elements(selector, locator)
            return elements
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in get selenium elements")

    def close_driver(self):
        self.driver.close()

    def press_key(self, key):
        self.driver.switch_to.active_element.send_keys(key)
