from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from models.database import get_db
from models.schemas import Stock, StockDetail
from services.data_import import get_available_stocks, import_all_stocks, get_stock_count, get_data_date_range
from services.stock_service import get_stock_details_service

router = APIRouter()


@router.get("/", response_model=List[Stock])
async def get_stocks(db: Session = Depends(get_db)):
    """Get list of all available stocks"""
    try:
        stocks = get_available_stocks(db)
        return stocks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stocks: {str(e)}")


@router.get("/count")
async def get_stocks_count(db: Session = Depends(get_db)):
    """Get total number of stocks"""
    try:
        count = get_stock_count(db)
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stock count: {str(e)}")


@router.get("/date-range")
async def get_date_range(
    symbol: Optional[str] = Query(None, description="Stock symbol to get date range for"),
    db: Session = Depends(get_db)
):
    """Get date range of available data"""
    try:
        date_range = get_data_date_range(db, symbol)
        return date_range
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving date range: {str(e)}")


@router.post("/import")
async def import_stock_data():
    """Import all stock data from CSV files"""
    try:
        result = import_all_stocks()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing stock data: {str(e)}")


@router.get("/{symbol}/details", response_model=StockDetail)
async def get_stock_details(
    symbol: str,
    simulated_date: Optional[str] = Query(None, description="Simulated current date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get detailed information for a specific stock"""
    try:
        return get_stock_details_service(db, symbol, simulated_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stock details: {str(e)}")