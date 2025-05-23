from datetime import datetime
import json
from src.services.google_alerts_service.google_alerts_service import (
    GoogleAlertsService,
)
from config.config import AppConfig
import pytest

service = GoogleAlertsService()
config = AppConfig()


@pytest.mark.order(1)
def test_check_cookies_validity():
    with open(GOOGLE_COOKIES_FILE, "r") as f:
        cookies = json.load(f)
    current_time = datetime.now().timestamp()
    for cookie in cookies:
        # Check required fields
        required_fields = ["name", "value", "domain"]
        for field in required_fields:
            assert field in cookie
        # Check expiration
        if "expiry" in cookie:
            assert cookie["expiry"] > current_time
