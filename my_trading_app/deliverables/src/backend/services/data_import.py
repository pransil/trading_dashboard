import os
import pandas as pd
from sqlalchemy.orm import Session
from models.database import get_db, Stock, StockData, SessionLocal
from typing import List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DATA_SOURCE_PATH = "/Users/patransil/dev/prediction/kaggle_stock_data"


def import_stock_from_csv(file_path: str, symbol: str, db: Session) -> bool:
    """Import a single stock's data from CSV file"""
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Validate required columns
        required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            logger.error(f"Missing required columns in {file_path}")
            return False
        
        # Create or get stock entry
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            stock = Stock(symbol=symbol, name=symbol)  # Use symbol as name for now
            db.add(stock)
            db.commit()
            db.refresh(stock)
        
        # Convert date column
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        
        # Delete existing data for this symbol first
        db.query(StockData).filter(StockData.symbol == symbol).delete()
        
        # Insert data in batches
        batch_size = 100
        total_records = len(df)
        
        for i in range(0, total_records, batch_size):
            batch_df = df.iloc[i:i+batch_size]
            stock_data_records = []
            
            for _, row in batch_df.iterrows():
                stock_data = StockData(
                    symbol=symbol,
                    date=row['Date'],
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    adj_close=float(row['Adj Close']),
                    volume=int(row['Volume'])
                )
                stock_data_records.append(stock_data)
            
            db.add_all(stock_data_records)
            db.commit()
        
        logger.info(f"Successfully imported {total_records} records for {symbol}")
        return True
        
    except Exception as e:
        logger.error(f"Error importing {file_path}: {str(e)}")
        db.rollback()
        return False


def import_all_stocks() -> dict:
    """Import all stocks from the CSV directory"""
    if not os.path.exists(DATA_SOURCE_PATH):
        logger.error(f"Data source path does not exist: {DATA_SOURCE_PATH}")
        return {"success": False, "message": "Data source path not found"}
    
    csv_files = [f for f in os.listdir(DATA_SOURCE_PATH) if f.endswith('.csv')]
    
    if not csv_files:
        logger.error(f"No CSV files found in {DATA_SOURCE_PATH}")
        return {"success": False, "message": "No CSV files found"}
    
    db = SessionLocal()
    try:
        successful_imports = 0
        failed_imports = 0
        
        for csv_file in csv_files:
            symbol = csv_file.replace('.csv', '').upper()
            file_path = os.path.join(DATA_SOURCE_PATH, csv_file)
            
            if import_stock_from_csv(file_path, symbol, db):
                successful_imports += 1
            else:
                failed_imports += 1
        
        logger.info(f"Import completed: {successful_imports} successful, {failed_imports} failed")
        
        return {
            "success": True,
            "total_files": len(csv_files),
            "successful_imports": successful_imports,
            "failed_imports": failed_imports
        }
        
    finally:
        db.close()


def get_available_stocks(db: Session) -> List[Stock]:
    """Get list of all available stocks"""
    return db.query(Stock).order_by(Stock.symbol).all()


def get_stock_count(db: Session) -> int:
    """Get total number of stocks in database"""
    return db.query(Stock).count()


def get_data_date_range(db: Session, symbol: str = None) -> dict:
    """Get the date range of available data"""
    query = db.query(StockData)
    if symbol:
        query = query.filter(StockData.symbol == symbol)
    
    if query.count() == 0:
        return {"min_date": None, "max_date": None}
    
    min_date = query.order_by(StockData.date.asc()).first().date
    max_date = query.order_by(StockData.date.desc()).first().date
    
    return {"min_date": min_date, "max_date": max_date}