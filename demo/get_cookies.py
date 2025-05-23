from src.services.google_alerts_service import google_alerts_service
from src.payloads.google_alerts_payload import *

service = google_alerts_service()
search_term = "Data scraping"
frequency = "Une fois par semaine maximum"
language = "français"
source = "Web"

service.save_session_cookies()
# def test_check_cookies_validity():
#     with open(GOOGLE_COOKIES_FILE, "r") as f:
#         cookies = json.load(f)
#     current_time = datetime.now().timestamp()
#     for cookie in cookies:
#         # Check required fields
#         required_fields = ["name", "value", "domain"]
#         for field in required_fields:
#             assert field in cookie
#         # Check expiration
#         if "expiry" in cookie:
#             assert cookie["expiry"] > current_time


# def test_set_alert():
#     payload = google_alerts_setting_payload(
#         search_term=search_term,
#         options=google_alerts_options(
#             frequency=frequency, language=language, source=source
#         ),
#     )
#     response = service.set_alert(payload)
#     assert response["status_code"] == 200


# # def test_remove_google_alerts():
# #     payload = google_alerts_deleting_payload(search_term=search_term)
# #     response = service.delete_existing_alerts(payload)
# #     assert response["status_code"] == 200
