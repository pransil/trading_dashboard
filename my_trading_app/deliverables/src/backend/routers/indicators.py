from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Callable, Any, Dict
from datetime import date, datetime

from models.database import get_db
from models.schemas import TechnicalIndicators
from services.indicator_calc import (
    get_ema_data, get_sma_data, get_rsi_data, get_obv_data, 
    get_vpt_data, get_vix_data, get_macd_data
)

router = APIRouter()


def parse_simulated_date(simulated_date: Optional[str]) -> Optional[date]:
    """Parse simulated date string"""
    if not simulated_date:
        return None
    
    try:
        return datetime.strptime(simulated_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")


def handle_indicator_request(
    indicator_func: Callable,
    db: Session,
    symbol: str,
    simulated_date: Optional[str] = None,
    timeframe: str = "1Y",
    **kwargs
) -> Dict[str, Any]:
    """Common handler for indicator requests"""
    try:
        sim_date = parse_simulated_date(simulated_date)
        result = indicator_func(db, symbol, simulated_date=sim_date, timeframe=timeframe, **kwargs)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating indicator: {str(e)}")


@router.get("/{symbol}/ema")
async def get_ema(
    symbol: str,
    period: int = Query(20, description="EMA period"),
    simulated_date: Optional[str] = Query(None, description="Simulated current date (YYYY-MM-DD)"),
    timeframe: Optional[str] = Query("1Y", description="Timeframe: 1W, 1M, 3M, 6M, 1Y, YTD, 5Y"),
    db: Session = Depends(get_db)
):
    """Get EMA (Exponential Moving Average) for a stock"""
    return handle_indicator_request(get_ema_data, db, symbol, simulated_date, timeframe, period=period)


@router.get("/{symbol}/sma")
async def get_sma(
    symbol: str,
    period: int = Query(20, description="SMA period"),
    simulated_date: Optional[str] = Query(None, description="Simulated current date (YYYY-MM-DD)"),
    timeframe: Optional[str] = Query("1Y", description="Timeframe: 1W, 1M, 3M, 6M, 1Y, YTD, 5Y"),
    db: Session = Depends(get_db)
):
    """Get SMA (Simple Moving Average) for a stock"""
    return handle_indicator_request(get_sma_data, db, symbol, simulated_date, timeframe, period=period)


@router.get("/{symbol}/rsi")
async def get_rsi(
    symbol: str,
    period: int = Query(14, description="RSI period"),
    simulated_date: Optional[str] = Query(None, description="Simulated current date (YYYY-MM-DD)"),
    timeframe: Optional[str] = Query("1Y", description="Timeframe: 1W, 1M, 3M, 6M, 1Y, YTD, 5Y"),
    db: Session = Depends(get_db)
):
    """Get RSI (Relative Strength Index) for a stock"""
    return handle_indicator_request(get_rsi_data, db, symbol, simulated_date, timeframe, period=period)


@router.get("/{symbol}/obv")
async def get_obv(
    symbol: str,
    simulated_date: Optional[str] = Query(None, description="Simulated current date (YYYY-MM-DD)"),
    timeframe: Optional[str] = Query("1Y", description="Timeframe: 1W, 1M, 3M, 6M, 1Y, YTD, 5Y"),
    db: Session = Depends(get_db)
):
    """Get OBV (On Balance Volume) for a stock"""
    return handle_indicator_request(get_obv_data, db, symbol, simulated_date, timeframe)


@router.get("/{symbol}/vpt")
async def get_vpt(
    symbol: str,
    simulated_date: Optional[str] = Query(None, description="Simulated current date (YYYY-MM-DD)"),
    timeframe: Optional[str] = Query("1Y", description="Timeframe: 1W, 1M, 3M, 6M, 1Y, YTD, 5Y"),
    db: Session = Depends(get_db)
):
    """Get VPT (Volume Price Trend) for a stock"""
    from services.indicator_calc import get_vpt_data
    from datetime import datetime
    
    # Parse simulated date
    sim_date = None
    if simulated_date:
        try:
            sim_date = datetime.strptime(simulated_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    result = get_vpt_data(db, symbol, sim_date, timeframe)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/{symbol}/vix")
async def get_vix(
    symbol: str,
    period: int = Query(20, description="Volatility calculation period"),
    simulated_date: Optional[str] = Query(None, description="Simulated current date (YYYY-MM-DD)"),
    timeframe: Optional[str] = Query("1Y", description="Timeframe: 1W, 1M, 3M, 6M, 1Y, YTD, 5Y"),
    db: Session = Depends(get_db)
):
    """Get VIX-like volatility indicator for a stock"""
    from services.indicator_calc import get_vix_data
    from datetime import datetime
    
    # Parse simulated date
    sim_date = None
    if simulated_date:
        try:
            sim_date = datetime.strptime(simulated_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    result = get_vix_data(db, symbol, period, sim_date, timeframe)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/{symbol}/macd")
async def get_macd(
    symbol: str,
    fast_period: int = Query(12, description="Fast EMA period"),
    slow_period: int = Query(26, description="Slow EMA period"),
    signal_period: int = Query(9, description="Signal line period"),
    simulated_date: Optional[str] = Query(None, description="Simulated current date (YYYY-MM-DD)"),
    timeframe: Optional[str] = Query("1Y", description="Timeframe"),
    db: Session = Depends(get_db)
):
    """Get MACD indicator for a stock"""
    from services.indicator_calc import get_macd_data
    from datetime import datetime
    
    # Parse simulated date
    sim_date = None
    if simulated_date:
        try:
            sim_date = datetime.strptime(simulated_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    result = get_macd_data(db, symbol, fast_period, slow_period, signal_period, sim_date, timeframe)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/{symbol}/all", response_model=List[TechnicalIndicators])
async def get_all_indicators(
    symbol: str,
    simulated_date: Optional[str] = Query(None, description="Simulated current date (YYYY-MM-DD)"),
    timeframe: Optional[str] = Query("1Y", description="Timeframe"),
    db: Session = Depends(get_db)
):
    """Get all technical indicators for a stock"""
    # This will be implemented once we have the indicators service
    raise HTTPException(status_code=501, detail="Technical indicators not implemented yet")