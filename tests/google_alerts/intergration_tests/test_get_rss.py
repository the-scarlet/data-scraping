from datetime import datetime
import json
from src.services.google_alerts_service.google_alerts_service import (
    GoogleAlertsService,
)
from config.config import AppConfig
import pytest

service = GoogleAlertsService()
config = AppConfig()


@pytest.mark.order(2)
def test_get_rss():
    response = service.get_rss_news()
    assert response == {"oil price", "oil demand", "crude price", "crude demand"}
