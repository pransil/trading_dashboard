#!/usr/bin/env python3
"""
Import a sample of stocks for testing
"""
import os
import sys
from pathlib import Path
sys.path.append('deliverables/src/backend')

from models.database import init_db, SessionLocal
from services.data_import import import_stock_from_csv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_sample_stocks():
    """Import a sample of stocks for testing"""
    # Initialize database
    init_db()
    
    # List of popular stocks to import for testing
    test_stocks = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL"]
    
    # Create session
    db = SessionLocal()
    
    try:
        successful = 0
        for symbol in test_stocks:
            csv_path = Path(__file__).parent / "data" / "kaggle_stock_data" / "stocks" / f"{symbol}.csv"
            if csv_path.exists():
                logger.info(f"Importing {symbol}...")
                result = import_stock_from_csv(str(csv_path), symbol, db)
                if result:
                    successful += 1
                    logger.info(f"✓ {symbol} imported successfully")
                else:
                    logger.error(f"✗ {symbol} import failed")
            else:
                logger.warning(f"CSV file not found for {symbol}")
        
        logger.info(f"Imported {successful}/{len(test_stocks)} stocks successfully")
        
    finally:
        db.close()

if __name__ == "__main__":
    import_sample_stocks()