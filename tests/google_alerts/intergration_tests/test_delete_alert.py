from src.services.google_alerts_service.google_alerts_service import (
    GoogleAlertsService,
)
import pytest

service = GoogleAlertsService()
instruments = ["oil"]
keywords = ["price"]


@pytest.mark.order(4)
def test_remove_google_alerts():
    response = service.delete_existing_alerts(
        instruments,
        keywords,
    )
    assert {"oil price"} <= response.get("Removed Alerts", {})
