from pydantic import BaseModel, ConfigDict
from datetime import date
from decimal import Decimal
from typing import List, Optional


class StockBase(BaseModel):
    symbol: str
    name: Optional[str] = None


class StockCreate(StockBase):
    pass


class Stock(StockBase):
    model_config = ConfigDict(from_attributes=True)


class StockDataBase(BaseModel):
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    adj_close: Decimal
    volume: int


class StockDataCreate(StockDataBase):
    symbol: str


class StockData(StockDataBase):
    id: int
    symbol: str
    
    model_config = ConfigDict(from_attributes=True)


class StockDataResponse(BaseModel):
    symbol: str
    data: List[StockData]
    
    model_config = ConfigDict(from_attributes=True)


class StockDetail(BaseModel):
    symbol: str
    name: Optional[str]
    current_price: Decimal
    change: Decimal
    change_percent: Decimal
    volume: int
    high_52w: Decimal
    low_52w: Decimal
    
    model_config = ConfigDict(from_attributes=True)


class WatchlistItem(BaseModel):
    symbol: str
    name: Optional[str]
    last_price: Decimal
    net_change: Decimal
    change_percent: Decimal
    volume: int
    
    model_config = ConfigDict(from_attributes=True)


class TechnicalIndicators(BaseModel):
    date: date
    ema: Optional[Decimal]
    macd: Optional[Decimal]
    macd_signal: Optional[Decimal]
    macd_histogram: Optional[Decimal]
    
    model_config = ConfigDict(from_attributes=True)


class SimulatedDateRequest(BaseModel):
    simulated_date: date


class TimeframeRequest(BaseModel):
    timeframe: str  # "1W", "1M", "3M", "6M", "1Y", "YTD", "5Y"