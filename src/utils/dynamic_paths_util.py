from datetime import datetime, timedelta
import os
from config.config import AppConfig

config = AppConfig()


class DynamicPaths:
    def path(self, topic, day_delay=0):
        today = datetime.now()
        target_day = today - timedelta(days=day_delay)

        # Extract components
        year = target_day.year
        month = target_day.month
        day = target_day.day
        # Full path
        full_path = os.path.join(
            config.google_alerts_output_path,
            "topic=" + topic,
            "year=" + str(year),
            "month=" + str(month),
            "day=" + str(day),
        )
        return full_path

    def most_recent_path(self, original_dir):
        embedded_dirs = [
            d
            for d in os.listdir(original_dir)
            if os.path.isdir(os.path.join(original_dir, d))
        ]
        if not embedded_dirs:
            return original_dir
        print("origianl dir: ", original_dir)
        print("list of dirs", embedded_dirs)
        most_recent_dir = max(embedded_dirs, key=lambda x: int(x.split("=")[1]))
        return self.most_recent_path(os.path.join(original_dir, most_recent_dir))
