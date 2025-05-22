from src.services.google_alerts_service.google_alerts_service import (
    GoogleAlertsService,
)

service = GoogleAlertsService()


def test_get_existing_google_alerts():
    response = service.get_existing_alerts()
    assert isinstance(response, str)
