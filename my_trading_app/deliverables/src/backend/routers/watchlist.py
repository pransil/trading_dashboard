from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from models.database import get_db
from models.schemas import WatchlistItem

router = APIRouter()


@router.get("/", response_model=List[WatchlistItem])
async def get_watchlist(
    symbols: str = Query(..., description="Comma-separated list of symbols (e.g., 'AAPL,TSLA,MSFT')"),
    simulated_date: Optional[str] = Query(None, description="Simulated current date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get watchlist data for multiple stocks"""
    from models.database import StockData, Stock
    from decimal import Decimal
    
    # Parse symbols
    symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
    
    if not symbol_list:
        raise HTTPException(status_code=400, detail="No symbols provided")
    
    # Parse simulated date
    sim_date = None
    if simulated_date:
        try:
            sim_date = datetime.strptime(simulated_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    watchlist_items = []
    
    for symbol in symbol_list:
        # Get current data for the symbol
        query = db.query(StockData).filter(StockData.symbol == symbol)
        
        if sim_date:
            query = query.filter(StockData.date <= sim_date)
        
        current_data = query.order_by(StockData.date.desc()).first()
        
        if not current_data:
            continue  # Skip symbols with no data
        
        # Get previous day's data for change calculation
        previous_data = db.query(StockData).filter(
            StockData.symbol == symbol,
            StockData.date < current_data.date
        ).order_by(StockData.date.desc()).first()
        
        # Calculate change and percentage
        net_change = Decimal(0)
        change_percent = Decimal(0)
        if previous_data:
            net_change = current_data.close - previous_data.close
            change_percent = (net_change / previous_data.close) * 100
        
        # Get stock name
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        stock_name = stock.name if stock else symbol
        
        watchlist_items.append(WatchlistItem(
            symbol=symbol,
            name=stock_name,
            last_price=current_data.close,
            net_change=net_change,
            change_percent=change_percent,
            volume=current_data.volume
        ))
    
    return watchlist_items