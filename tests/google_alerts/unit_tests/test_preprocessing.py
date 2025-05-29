from src.services.google_alerts_service.preprocessing.preprocessing import (
    GoogleAlertsPreprocessing,
)
import pytest
from src.utils.selenium_util.selenium_util import SeleniumUtil
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

selenium = SeleniumUtil()
preprocessing = GoogleAlertsPreprocessing()


@pytest.mark.order(1)
def test_google_login():
    preprocessing.google_login(selenium)


@pytest.mark.order(2)
def test_are_there_google_alerts():
    preprocessing.are_there_google_alerts(selenium)


@pytest.mark.order(3)
def test_are_there_rss_alerts():
    preprocessing.are_there_rss_alerts(selenium)


def test_commodities():
    instruments = ["oil", "crude"]
    keywords = ["price", "demand"]
    commodities = preprocessing.commodities(instruments, keywords)
    assert commodities == ["oil price", "oil demand", "crude price", "crude demand"]


def test_map_selector():
    selector = selenium.map_selector("by_css")
    assert selector == By.CSS_SELECTOR


def test_map_selenium_condition():
    condition = selenium.map_selenium_condition("presence_of_all_elements_located")
    assert condition == EC.presence_of_all_elements_located


def test_close_driver():
    selenium.close_driver()
