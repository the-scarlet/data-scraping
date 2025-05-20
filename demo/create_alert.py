from src.services.google_alerts_service import google_alerts_service
from src.payloads.google_alerts_payload import *

service = google_alerts_service()
search_term = "Data scraping"
frequency = "Une fois par semaine maximum"
language = "français"
source = "Web"


payload = google_alerts_setting_payload(
    search_term=search_term,
    options=google_alerts_options(
        frequency=frequency, language=language, source=source
    ),
)
service.set_alert(payload)
