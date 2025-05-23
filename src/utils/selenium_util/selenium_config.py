from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os

CHROME_BINARY_LOCATION = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "chrome-win64", "chrome.exe")
)  # "/src/utils/selenium_util/chrome-win64/chrome.exe"
TIMEOUT = 10  # 10s
SELECTORS = {
    "by_id": By.ID,  # Finds element by HTML ID
    "by_name": By.NAME,  # Finds element by 'name' attribute
    "by_class": By.CLASS_NAME,  # Finds by CSS class
    "by_tag": By.TAG_NAME,  # Finds by HTML tag (e.g., <input>)
    "by_link_text": By.LINK_TEXT,  # Finds <a> by exact text
    "by_partial_link_text": By.PARTIAL_LINK_TEXT,  # Partial link text
    "by_css": By.CSS_SELECTOR,  # CSS Selector (powerful)
    "by_xpath": By.XPATH,  # XPath (flexible)
}
EXPECTED_CONDITION = {
    "presence_of_all_elements_located": EC.presence_of_all_elements_located,
    "element_to_be_clickable": EC.element_to_be_clickable,
    "text_to_be_present_in_element_value": EC.text_to_be_present_in_element_value,
}
# Set chromium language (french)
CHROMIUM_COUNTRY_LANGUAGE = "fr-FR"

# disable telemetry
os.environ["SE_AVOID_STATS"] = "true"
