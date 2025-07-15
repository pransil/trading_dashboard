import os
from pathlib import Path

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trading_dashboard.db")

# Data paths
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
KAGGLE_DATA_PATH = DATA_DIR / "kaggle_stock_data" / "stocks"

# CORS configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
]

# API configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
API_RELOAD = True

# Logging configuration
LOG_LEVEL = "INFO"