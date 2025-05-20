import pandas as pd
from ..services.google_alerts_service import google_alerts_service
from ..utils.error_util import error_util


async def set_google_alerts(args):
    # try:
    _scraper = google_alerts_service()

    response = _scraper.set_alert(
        args.instruments,
        args.keywords,
        args.frequency,
        args.source,
        args.language,
        args.region,
        args.volume,
        args.delivery,
    )
    return response


# except ValueError as ve:
#     return error_util.handle_error(
#         ve, "Validation Error in TranslateHtml controller", 400
#     )
# except Exception as e:
#     return error_util.handle_error(e, "Error in TranslateHtml controller", 500)


async def get_existing_google_alerts():
    # try:
    _scraper = google_alerts_service()
    response = _scraper.get_existing_alerts()
    return f"Active alerts: {response}"


# except ValueError as ve:
#     return error_util.handle_error(
#         ve, "Validation Error in TranslateHtml controller", 400
#     )
# except Exception as e:
#     return error_util.handle_error(e, "Error in TranslateHtml controller", 500)


async def remove_google_alerts(args):
    # try:
    _scraper = google_alerts_service()
    response = _scraper.delete_existing_alerts(
        args.instruments,
        args.keywords,
    )
    return response


# except ValueError as ve:
#     return error_util.handle_error(
#         ve, "Validation Error in TranslateHtml controller", 400
#     )
# except Exception as e:
#     return error_util.handle_error(e, "Error in TranslateHtml controller", 500)


async def scrape_google_alerts(args):
    try:
        _scraper = google_alerts_service()
        return _scraper.get_alert(args)  # jsonable_encoder({"url_list": url_list})
    except ValueError as ve:
        return error_util.handle_error(
            ve, "Validation Error in TranslateHtml controller", 400
        )
    except Exception as e:
        return error_util.handle_error(e, "Error in TranslateHtml controller", 500)


async def get_cookies():
    # try:
    _scraper = google_alerts_service()
    results = _scraper.save_session_cookies()
    return {"results": results}


# except ValueError as ve:
#     return error_util.handle_error(
#         ve, "Validation Error in TranslateHtml controller", 400
#     )
# except Exception as e:
#     return error_util.handle_error(e, "Error in TranslateHtml controller", 500)


async def get_rss_links():
    # try:
    _scraper = google_alerts_service()
    results = _scraper.get_rss_news()
    df = pd.DataFrame(results)

    # Save to CSV
    df.to_excel("google_alerts_news.xlsx", index=False)

    print("CSV file saved successfully!")

    return {"results": results}
