"""
Stock service for business logic
"""
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional

from models.database import StockData
from models.schemas import StockDetail


def parse_simulated_date(simulated_date: str) -> date:
    """Parse simulated date string into date object"""
    try:
        return datetime.strptime(simulated_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD")


def get_latest_available_date(db: Session, symbol: str) -> date:
    """Get the latest available date for a symbol"""
    latest_data = db.query(StockData).filter(
        StockData.symbol == symbol.upper()
    ).order_by(StockData.date.desc()).first()
    
    if not latest_data:
        raise ValueError(f"No data found for symbol {symbol}")
    
    return latest_data.date


def get_stock_data_for_date(db: Session, symbol: str, target_date: date) -> StockData:
    """Get stock data for a specific date or closest available date before it"""
    stock_data = db.query(StockData).filter(
        StockData.symbol == symbol.upper(),
        StockData.date <= target_date
    ).order_by(StockData.date.desc()).first()
    
    if not stock_data:
        raise ValueError(f"No data found for {symbol} on or before {target_date}")
    
    return stock_data


def calculate_price_change(current_data: StockData, db: Session) -> tuple[Decimal, Decimal]:
    """Calculate price change and percentage change"""
    previous_data = db.query(StockData).filter(
        StockData.symbol == current_data.symbol,
        StockData.date < current_data.date
    ).order_by(StockData.date.desc()).first()
    
    if not previous_data:
        return Decimal(0), Decimal(0)
    
    change = current_data.close - previous_data.close
    change_percent = (change / previous_data.close) * 100
    
    return change, change_percent


def calculate_52_week_range(db: Session, symbol: str, target_date: date) -> tuple[Decimal, Decimal]:
    """Calculate 52-week high and low"""
    year_ago = target_date - timedelta(days=365)
    year_data = db.query(StockData).filter(
        StockData.symbol == symbol.upper(),
        StockData.date >= year_ago,
        StockData.date <= target_date
    ).all()
    
    if not year_data:
        # Fallback to current data if no year data available
        current_data = get_stock_data_for_date(db, symbol, target_date)
        return current_data.high, current_data.low
    
    high_52w = max(d.high for d in year_data)
    low_52w = min(d.low for d in year_data)
    
    return high_52w, low_52w


def get_stock_details_service(
    db: Session, 
    symbol: str, 
    simulated_date: Optional[str] = None
) -> StockDetail:
    """Get detailed stock information"""
    # Parse or get latest date
    if simulated_date:
        sim_date = parse_simulated_date(simulated_date)
    else:
        sim_date = get_latest_available_date(db, symbol)
    
    # Get current stock data
    current_data = get_stock_data_for_date(db, symbol, sim_date)
    
    # Calculate price changes
    change, change_percent = calculate_price_change(current_data, db)
    
    # Calculate 52-week range
    high_52w, low_52w = calculate_52_week_range(db, symbol, sim_date)
    
    return StockDetail(
        symbol=symbol.upper(),
        name=symbol.upper(),  # TODO: Get actual company name from database
        current_price=current_data.close,
        change=change,
        change_percent=change_percent,
        volume=current_data.volume,
        high_52w=high_52w,
        low_52w=low_52w
    )