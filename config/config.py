import os
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class AppConfig:
    """Application configuration for Google Alerts scraping"""

    # Logging configuration
    log_level: str = "INFO"

    # Path configuration
    home_path: str = os.environ.get("HOME") or os.environ.get("USERPROFILE")
    artefacts_directory: str = "data_scraping_artefacts"

    # File names (not paths)
    google_cookies_file: str = "cookies.json"
    news_excel_file_name: str = "google_alerts_news.xlsx"
    news_parquet_file_name: str = "google_alerts_news.parquet"

    # Google Alerts defaults
    default_entry: ClassVar[str] = "DEFAULT"
    frequency: ClassVar[str] = "Quand le cas se présente"
    source: ClassVar[str] = "Automatique"
    language: ClassVar[str] = "Toutes les langues"
    region: ClassVar[str] = "Toutes les régions"
    volume: ClassVar[str] = "Tous les résultats"
    delivery: ClassVar[str] = default_entry

    def __post_init__(self):
        """Validate paths and create directories/files if needed"""
        if not self.home_path:
            raise ValueError("Could not find home directory")

        # Create artefacts directory if it doesn't exist
        os.makedirs(self.artefacts_path, exist_ok=True)

        # Initialize files if they don't exist
        for file_name in [
            self.google_cookies_file,
            self.news_excel_file_name,
            self.news_parquet_file_name,
        ]:
            file_path = os.path.join(self.artefacts_path, file_name)
            if not os.path.exists(file_path):
                if file_name.endswith(".json"):
                    with open(file_path, "w") as f:
                        f.write("{}")
                elif file_name.endswith((".xlsx", ".parquet")):
                    open(file_path, "a").close()

    @property
    def artefacts_path(self) -> str:
        """Get the full path to the artefacts directory"""
        return os.path.join(self.home_path, self.artefacts_directory)

    @property
    def cookies_path(self) -> str:
        """Get full path to cookies file"""
        return os.path.join(self.artefacts_path, self.google_cookies_file)

    @property
    def excel_path(self) -> str:
        """Get full path to Excel file"""
        return os.path.join(self.artefacts_path, self.news_excel_file_name)

    @property
    def parquet_path(self) -> str:
        """Get full path to Parquet file"""
        return os.path.join(self.artefacts_path, self.news_parquet_file_name)
