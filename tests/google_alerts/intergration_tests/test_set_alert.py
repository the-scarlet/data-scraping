from datetime import datetime
import json
from src.services.google_alerts_service.google_alerts_service import (
    GoogleAlertsService,
)
from config.config import AppConfig
import pytest

service = GoogleAlertsService()
config = AppConfig()
instruments = ["oil", "crude"]
keywords = ["price", "demand"]
frequency = "Une fois par semaine maximum"
language = "français"
source = "Web"


@pytest.mark.order(2)
def test_set_alert():
    response = service.set_alert(
        instruments,
        keywords,
        config.frequency,
        config.source,
        config.language,
        config.region,
        config.volume,
        config.delivery,
    )
    assert response == {"oil price", "oil demand", "crude price", "crude demand"}
