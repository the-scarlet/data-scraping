import pandas as pd
from src.services.google_alerts_service.google_alerts_service import (
    GoogleAlertsService,
)
from src.utils.error_util import ErrorUtil
from config.config import AppConfig

config = AppConfig()


async def set_google_alerts(args):
    try:
        _scraper = GoogleAlertsService()

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

    except Exception as e:
        return ErrorUtil.handle_error(e, "Error in set alert controller")


async def get_existing_google_alerts():
    try:
        _scraper = GoogleAlertsService()
        response = _scraper.get_existing_alerts()

        return f"Active alerts: {response}"
    except Exception as e:
        return ErrorUtil.handle_error(e, "Error in get existing alerts controller")


async def remove_google_alerts(args):
    try:
        _scraper = GoogleAlertsService()
        response = _scraper.delete_existing_alerts(
            args.instruments,
            args.keywords,
        )
        return response
    except Exception as e:
        return ErrorUtil.handle_error(e, "Error in remove alerts controller")


async def scrape_google_alerts(args):
    try:
        _scraper = GoogleAlertsService()
        return _scraper.get_alert(args)  # jsonable_encoder({"url_list": url_list})
    except Exception as e:
        return ErrorUtil.handle_error(e, "Error in scrape alert controller")


async def get_cookies():
    try:
        _scraper = GoogleAlertsService()
        results = _scraper.save_session_cookies()
        return {"results": results}

    except Exception as e:
        return ErrorUtil.handle_error(e, "Error in get cookies controller")


async def get_rss_links():
    try:
        _scraper = GoogleAlertsService()
        results = _scraper.get_rss_news()

        # Save to Excel/ Parquet
        results.to_excel(config.excel_path, index=False)
        results.to_parquet(config.parquet_path, engine="pyarrow")
        return "File saved successfully!"
    except Exception as e:
        return ErrorUtil.handle_error(e, "Error in get RSS links controller")
