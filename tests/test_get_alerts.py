from src.services.google_alerts_service import google_alerts_service

service = google_alerts_service()


def test_get_existing_google_alerts():
    response = service.get_existing_alerts()
    assert isinstance(response, str)
