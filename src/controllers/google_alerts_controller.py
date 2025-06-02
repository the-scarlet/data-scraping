import os
import pandas as pd
from src.services.google_alerts_service.google_alerts_service import (
    GoogleAlertsService,
)
from src.utils.logger import logging
from src.utils.error_util import ErrorUtil
from config.config import AppConfig
from datetime import datetime
from src.utils.dynamic_paths_util import DynamicPaths

config = AppConfig()

logger = logging.getLogger("Data-scraping")


async def set_google_alerts(args):
    # try:
    _scraper = await GoogleAlertsService.create()

    response = await _scraper.set_alert(
        args.instruments,
        args.keywords,
        args.frequency,
        args.source,
        args.language,
        args.region,
        args.volume,
        args.delivery,
    )
    return (
        f"Request processed successfully. You will get alerts for the terms {response}."
    )


# except Exception as e:
#     return ErrorUtil.handle_error(e, "Error in set alert controller")


async def get_existing_google_alerts():
    # try:
    _scraper = await GoogleAlertsService.create()
    response = await _scraper.get_existing_alerts()

    return f"Active alerts: {response}"


# except Exception as e:
#     return ErrorUtil.handle_error(e, "Error in get existing alerts controller")


async def remove_google_alerts(args):
    # try:
    _scraper = await GoogleAlertsService.create()
    response = await _scraper.delete_existing_alerts(
        args.instruments,
        args.keywords,
    )
    return response


# except Exception as e:
#     return ErrorUtil.handle_error(e, "Error in remove alerts controller")


async def scrape_google_alerts(args):
    try:
        _scraper = await GoogleAlertsService()
        return _scraper.get_alert(args)  # jsonable_encoder({"url_list": url_list})
    except Exception as e:
        return ErrorUtil.handle_error(e, "Error in scrape alert controller")


async def get_cookies():
    # try:
    _scraper = await GoogleAlertsService.create()
    results = await _scraper.save_session_cookies()
    return {"results": results}


# except Exception as e:
#     return ErrorUtil.handle_error(e, "Error in get cookies controller")


async def get_rss_links():
    # try:
    _scraper = await GoogleAlertsService.create()
    results = await _scraper.get_rss_news()
    if results.empty:
        return "There is no new RSS feed, try again later"
    for topic in results["Topic"].unique():
        # Full path
        full_path = DynamicPaths().path(topic)
        os.makedirs(full_path, exist_ok=True)
        # Save to Excel/ Parquet
        spcific_topic_news = results[results["Topic"] == topic]
        spcific_topic_news.to_excel(
            os.path.join(
                full_path,
                "google_alerts.xlsx",
            ),
            index=False,
        )
        spcific_topic_news.to_parquet(
            os.path.join(full_path, "google_alerts.parquet"), engine="pyarrow"
        )
    return "Files saved successfully!"


# except Exception as e:
#     return ErrorUtil.handle_error(e, "Error in get RSS links controller")
