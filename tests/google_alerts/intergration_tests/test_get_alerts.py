from src.services.google_alerts_service.google_alerts_service import (
    GoogleAlertsService,
)
import pytest

service = GoogleAlertsService()


@pytest.mark.order(3)
def test_get_existing_google_alerts():
    response = service.get_existing_alerts()
    assert {"oil price", "oil demand", "crude price", "crude demand"} <= response
