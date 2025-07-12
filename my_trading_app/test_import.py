#!/usr/bin/env python3
"""
Test data import for a single stock
"""
import os
import sys
sys.path.append('deliverables/src/backend')

from models.database import init_db, SessionLocal
from services.data_import import import_stock_from_csv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_import():
    """Test importing a single stock"""
    # Initialize database
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Test with AAPL (likely to exist and have good data)
        csv_path = "/Users/patransil/dev/prediction/kaggle_stock_data/AAPL.csv"
        if os.path.exists(csv_path):
            logger.info("Testing import of AAPL...")
            result = import_stock_from_csv(csv_path, "AAPL", db)
            if result:
                logger.info("Import successful!")
            else:
                logger.error("Import failed!")
        else:
            logger.error(f"CSV file not found: {csv_path}")
    finally:
        db.close()

if __name__ == "__main__":
    test_single_import()