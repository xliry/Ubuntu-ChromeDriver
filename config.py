"""
Ubuntu Chrome Automation Configuration
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
PROFILES_DIR = BASE_DIR / "profiles"
DOWNLOADS_DIR = BASE_DIR / "downloads"

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR, PROFILES_DIR, DOWNLOADS_DIR]:
    directory.mkdir(exist_ok=True)

# Chrome Configuration
CHROME_CONFIG = {
    "headless": False,  # Set to True for server environments
    "no_sandbox": True,
    "disable_dev_shm_usage": True,
    "disable_gpu": True,
    "disable_extensions": True,
    "disable_plugins": True,
    "disable_images": False,  # Keep images for better detection
    "disable_javascript": False,  # Keep JS for Flow functionality
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Session Configuration
SESSION_CONFIG = {
    "credit_threshold": 20,  # Minimum credits before account switch
    "session_timeout_hours": 24,
    "encryption_key_file": ".encryption_key",
    "session_file": "session_data.json"
}

# Flow Configuration
FLOW_CONFIG = {
    "base_url": "https://labs.google/fx/tools/flow",
    "login_url": "https://accounts.google.com/signin",
    "wait_timeout": 20,
    "project_creation_delay": 5,
    "video_quality": "720p"
}

# Account Pool Configuration
ACCOUNT_CONFIG = {
    "max_concurrent_accounts": 5,
    "account_rotation_delay": 300,  # 5 minutes
    "max_login_attempts": 3
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": LOGS_DIR / "automation.log"
}

# Environment variables
ENV_VARS = {
    "GOOGLE_EMAIL": os.getenv("GOOGLE_EMAIL"),
    "GOOGLE_PASSWORD": os.getenv("GOOGLE_PASSWORD"),
    "CHROME_HEADLESS": os.getenv("CHROME_HEADLESS", "false").lower() == "true"
}


