from src.services.google_alerts_service import google_alerts_service

service = google_alerts_service()
search_term = instruments = ["oil", "crude"]
keywords = ["price", "demand"]


def test_remove_google_alerts():
    response = service.delete_existing_alerts(
        instruments,
        keywords,
    )
    assert isinstance(response, str)
