from datetime import datetime
import os
import pytest
from config.config import AppConfig
from src.utils.dynamic_paths_util import DynamicPaths

paths = DynamicPaths()

config = AppConfig()


def test_path():
    topic = "Oil"
    today_path = paths.path(topic)

    today = datetime.now()

    # Extract components
    year = today.year
    month = today.month
    day = today.day
    # Full path
    actual_path = os.path.join(
        config.google_alerts_output_path,
        "topic=" + topic,
        "year=" + str(year),
        "month=" + str(month),
        "day=" + str(day),
    )
    assert actual_path == today_path
