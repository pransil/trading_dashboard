from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta

from models.database import get_db, StockData
from models.schemas import StockData as StockDataSchema, StockDataResponse

router = APIRouter()


@router.get("/{symbol}", response_model=StockDataResponse)
async def get_stock_data(
    symbol: str,
    simulated_date: Optional[str] = Query(None, description="Simulated current date (YYYY-MM-DD)"),
    timeframe: Optional[str] = Query("1Y", description="Timeframe: 1W, 1M, 3M, 6M, 1Y, YTD, 5Y"),
    db: Session = Depends(get_db)
):
    """Get OHLC data for a specific stock with date filtering"""
    try:
        # Parse simulated date
        sim_date = None
        if simulated_date:
            try:
                sim_date = datetime.strptime(simulated_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            # Use latest available date if no simulated date provided
            latest_data = db.query(StockData).filter(
                StockData.symbol == symbol.upper()
            ).order_by(StockData.date.desc()).first()
            
            if latest_data:
                sim_date = latest_data.date
            else:
                raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        # Calculate start date based on timeframe
        start_date = calculate_start_date(sim_date, timeframe)
        
        # Query data with date filtering (no future data)
        query = db.query(StockData).filter(
            StockData.symbol == symbol.upper(),
            StockData.date <= sim_date,
            StockData.date >= start_date
        ).order_by(StockData.date.asc())
        
        stock_data = query.all()
        
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol} in the specified timeframe")
        
        return StockDataResponse(
            symbol=symbol.upper(),
            data=stock_data
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stock data: {str(e)}")


def calculate_start_date(simulated_date: date, timeframe: str) -> date:
    """Calculate start date based on timeframe"""
    if timeframe == "1W":
        return simulated_date - timedelta(weeks=1)
    elif timeframe == "1M":
        return simulated_date - timedelta(days=30)
    elif timeframe == "3M":
        return simulated_date - timedelta(days=90)
    elif timeframe == "6M":
        return simulated_date - timedelta(days=180)
    elif timeframe == "1Y":
        return simulated_date - timedelta(days=365)
    elif timeframe == "YTD":
        return date(simulated_date.year, 1, 1)
    elif timeframe == "5Y":
        return simulated_date - timedelta(days=1825)
    else:
        # Default to 1 year
        return simulated_date - timedelta(days=365)