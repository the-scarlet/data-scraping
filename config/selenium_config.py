import os
from dataclasses import dataclass, field
from typing import Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


@dataclass(frozen=True)
class SeleniumConfig:
    """Configuration for Selenium WebDriver setup"""

    # Path configuration
    chrome_binary_location: str = os.path.abspath(
        os.path.join("src", "utils", "selenium_util", "chrome-win64", "chrome.exe")
    )

    # Timeout settings
    timeout: int = 10  # seconds

    # Selector types
    selectors: Dict[str, Any] = field(
        default_factory=lambda: {
            "by_id": By.ID,
            "by_name": By.NAME,
            "by_class": By.CLASS_NAME,
            "by_tag": By.TAG_NAME,
            "by_link_text": By.LINK_TEXT,
            "by_partial_link_text": By.PARTIAL_LINK_TEXT,
            "by_css": By.CSS_SELECTOR,
            "by_xpath": By.XPATH,
        }
    )

    # Expected conditions
    expected_conditions: Dict[str, Any] = field(
        default_factory=lambda: {
            "presence_of_all_elements_located": EC.presence_of_all_elements_located,
            "element_to_be_clickable": EC.element_to_be_clickable,
            "text_to_be_present_in_element_value": EC.text_to_be_present_in_element_value,
        }
    )

    # Browser settings
    chromium_country_language: str = "fr-FR"

    def __post_init__(self):
        """Validate configuration on initialization"""
        # Set environment variables
        os.environ["SE_AVOID_STATS"] = "true"

        # Verify Chrome binary exists
        if not os.path.exists(self.chrome_binary_location):
            raise FileNotFoundError(
                f"Chrome binary not found at: {self.chrome_binary_location}"
            )
