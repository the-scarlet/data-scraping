import os
from dataclasses import dataclass, field
from typing import Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path


@dataclass(frozen=True)
class PlaywrightConfig:
    """Configuration for Selenium WebDriver setup"""

    project_root = Path(__file__).parent.parent
    # Path configuration

    # Timeout settings
    timeout: int = 10000  # seconds

    # Browser settings
    chromium_country_language: str = "fr-FR"
