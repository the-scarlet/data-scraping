from datetime import datetime
import json
from src.services.google_alerts_service import google_alerts_service
from src.config import (
    GOOGLE_COOKIES_FILE,
    FREQUENCY,
    SOURCE,
    LANGUAGE,
    VOLUME,
    REGION,
    DELIVERY,
)

service = google_alerts_service()
instruments = ["oil", "crude"]
keywords = ["price", "demand"]
frequency = "Une fois par semaine maximum"
language = "français"
source = "Web"


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


def test_set_alert():
    response = service.set_alert(
        instruments, keywords, FREQUENCY, SOURCE, LANGUAGE, REGION, VOLUME, DELIVERY
    )
    assert isinstance(response, str)
