from src.services.google_alerts_service.google_alerts_service import (
    GoogleAlertsService,
)

service = GoogleAlertsService()
search_term = instruments = ["oil", "crude"]
keywords = ["price", "demand"]


def test_remove_google_alerts():
    response = service.delete_existing_alerts(
        instruments,
        keywords,
    )
    assert isinstance(response, str)
