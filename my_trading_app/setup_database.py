#!/usr/bin/env python3
"""
Setup script for Trading Dashboard database and data import
"""
import os
import sys
sys.path.append('deliverables/src/backend')

from sqlalchemy import create_engine
from models.database import Base, init_db
from services.data_import import import_all_stocks
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration (using SQLite for simplicity)
DATABASE_URL = "sqlite:///./trading_dashboard.db"

def create_database():
    """Create/check SQLite database"""
    try:
        # SQLite databases are created automatically
        logger.info("Using SQLite database - no setup required")
        return True
    except Exception as e:
        logger.error(f"Error with database: {str(e)}")
        return False

def setup_tables():
    """Initialize database tables"""
    try:
        os.environ["DATABASE_URL"] = DATABASE_URL
        init_db()
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        return False

def import_data():
    """Import stock data from CSV files"""
    try:
        result = import_all_stocks()
        if result["success"]:
            logger.info(f"Data import completed: {result}")
        else:
            logger.error(f"Data import failed: {result}")
        return result["success"]
    except Exception as e:
        logger.error(f"Error importing data: {str(e)}")
        return False

def main():
    """Main setup function"""
    logger.info("Starting Trading Dashboard setup...")
    
    # Step 1: Create database
    if not create_database():
        logger.error("Failed to create database. Exiting.")
        sys.exit(1)
    
    # Set environment variable for the application
    os.environ["DATABASE_URL"] = DATABASE_URL
    
    # Step 2: Create tables
    if not setup_tables():
        logger.error("Failed to create tables. Exiting.")
        sys.exit(1)
    
    # Step 3: Import data
    logger.info("Starting data import...")
    if not import_data():
        logger.error("Data import failed. Exiting.")
        sys.exit(1)
    
    logger.info("Setup completed successfully!")
    logger.info(f"Database URL: {DATABASE_URL}")
    logger.info("You can now start the backend server with:")
    logger.info("cd deliverables/src/backend && uvicorn main:app --reload")

if __name__ == "__main__":
    main()