from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from ...utils.error_util import error_util
from ...utils.selenium_util.selenium_config import (
    CHROME_BINARY_LOCATION,
    TIMEOUT,
    SELECTORS,
    CHROMIUM_COUNTRY_LANGUAGE,
    EXPECTED_CONDITION,
)


class selenium_util:
    def __init__(self):
        # Set path to your Chrome binary
        chrome_options = Options()
        chrome_options.binary_location = CHROME_BINARY_LOCATION

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
        chrome_options.add_argument(f"--lang={CHROMIUM_COUNTRY_LANGUAGE}")

        # If needed, use a completely temporary profile
        # chrome_options.add_argument("--user-data-dir=./temp_profile")

        # Initialize WebDriver with options
        self.driver = webdriver.Chrome(options=chrome_options)

        # to type sth using keyboard
        self.keys = Keys

    def get_url(self, url):
        self.driver.get(url)

    def map_selector(self, selection_method):
        return SELECTORS[selection_method]

    def map_selenium_condition(self, condition):
        return EXPECTED_CONDITION[condition]

    def wait_for(
        self,
        wait_condition,
        selection_method,
        locator,
        timeout=TIMEOUT,
        has_special_error_handler=False,
    ):
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
                error_util.handle_error(
                    e,
                    "This exception is the result of not finding an element in the page.",
                )
                exit(1)
        return element

    def set_text_input_value(self, selection_method, locator, text, timeout=TIMEOUT):
        text_input = self.wait_for(
            "element_to_be_clickable", selection_method, locator, timeout
        )
        text_input.send_keys(text)

    def click_button(self, selection_method, locator, timeout=TIMEOUT):
        button = self.wait_for(
            "element_to_be_clickable", selection_method, locator, timeout
        )
        button.click()

    def get_elements(self, selection_method, locator, timeout=TIMEOUT):
        selector = self.map_selector(selection_method)
        self.wait_for(
            "presence_of_all_elements_located", selection_method, locator, timeout
        )
        elements = self.driver.find_elements(selector, locator)
        return elements

    def close_driver(self):
        self.driver.close()

    def press_key(self, key):
        self.driver.switch_to.active_element.send_keys(key)
