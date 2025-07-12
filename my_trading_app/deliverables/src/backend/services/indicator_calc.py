"""
Technical indicators calculation service
"""
import pandas as pd
from typing import List, Dict, Any
from datetime import date
from decimal import Decimal
import numpy as np
from sqlalchemy.orm import Session
from models.database import StockData


def calculate_ema(data: List[float], period: int) -> List[float]:
    """Calculate Exponential Moving Average"""
    if len(data) < period:
        return [None] * len(data)
    
    # Convert to pandas Series for easier calculation
    series = pd.Series(data)
    ema = series.ewm(span=period, adjust=False).mean()
    
    # Return as list, with None for initial periods
    result = [None] * (period - 1) + ema.iloc[period - 1:].tolist()
    return result


def calculate_sma(data: List[float], period: int) -> List[float]:
    """Calculate Simple Moving Average"""
    if len(data) < period:
        return [None] * len(data)
    
    # Convert to pandas Series for easier calculation
    series = pd.Series(data)
    sma = series.rolling(window=period).mean()
    
    # Return as list
    return sma.tolist()


def calculate_rsi(data: List[float], period: int = 14) -> List[float]:
    """Calculate Relative Strength Index"""
    if len(data) < period + 1:
        return [None] * len(data)
    
    # Convert to pandas Series
    series = pd.Series(data)
    
    # Calculate price changes
    delta = series.diff()
    
    # Separate gains and losses
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    
    # Calculate average gains and losses
    avg_gains = gains.rolling(window=period).mean()
    avg_losses = losses.rolling(window=period).mean()
    
    # Calculate RSI
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.tolist()


def calculate_volatility(data: List[float], period: int = 20) -> List[float]:
    """Calculate volatility (VIX-like) using rolling standard deviation of returns"""
    if len(data) < period + 1:
        return [None] * len(data)
    
    # Convert to pandas Series
    series = pd.Series(data)
    
    # Calculate daily returns (percentage change)
    returns = series.pct_change()
    
    # Calculate rolling standard deviation of returns and annualize it
    volatility = returns.rolling(window=period).std() * np.sqrt(252) * 100  # Annualized volatility in %
    
    return volatility.tolist()


def calculate_obv(close_prices: List[float], volumes: List[float]) -> List[float]:
    """Calculate On Balance Volume"""
    if len(close_prices) != len(volumes) or len(close_prices) < 2:
        return [None] * len(close_prices)
    
    obv = [0]  # Start with 0
    
    for i in range(1, len(close_prices)):
        if close_prices[i] > close_prices[i-1]:
            # Price went up, add volume
            obv.append(obv[-1] + volumes[i])
        elif close_prices[i] < close_prices[i-1]:
            # Price went down, subtract volume
            obv.append(obv[-1] - volumes[i])
        else:
            # Price unchanged, OBV unchanged
            obv.append(obv[-1])
    
    return obv


def calculate_vpt(close_prices: List[float], volumes: List[float]) -> List[float]:
    """Calculate Volume Price Trend"""
    if len(close_prices) != len(volumes) or len(close_prices) < 2:
        return [None] * len(close_prices)
    
    vpt = [0]  # Start with 0
    
    for i in range(1, len(close_prices)):
        if close_prices[i-1] != 0:  # Avoid division by zero
            price_change_pct = (close_prices[i] - close_prices[i-1]) / close_prices[i-1]
            vpt.append(vpt[-1] + (volumes[i] * price_change_pct))
        else:
            vpt.append(vpt[-1])
    
    return vpt


def calculate_macd(data: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, List[float]]:
    """Calculate MACD (Moving Average Convergence Divergence)"""
    if len(data) < slow_period:
        return {
            'macd': [None] * len(data),
            'signal': [None] * len(data),
            'histogram': [None] * len(data)
        }
    
    # Calculate EMAs
    ema_fast = calculate_ema(data, fast_period)
    ema_slow = calculate_ema(data, slow_period)
    
    # Calculate MACD line (difference between fast and slow EMA)
    macd_line = []
    for i in range(len(data)):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            macd_line.append(ema_fast[i] - ema_slow[i])
        else:
            macd_line.append(None)
    
    # Calculate signal line (EMA of MACD line)
    macd_values = [x for x in macd_line if x is not None]
    if len(macd_values) >= signal_period:
        signal_ema = calculate_ema(macd_values, signal_period)
        # Pad with None values for the initial period
        signal_line = [None] * (len(macd_line) - len(signal_ema)) + signal_ema
    else:
        signal_line = [None] * len(data)
    
    # Calculate histogram (MACD - Signal)
    histogram = []
    for i in range(len(data)):
        if macd_line[i] is not None and signal_line[i] is not None:
            histogram.append(macd_line[i] - signal_line[i])
        else:
            histogram.append(None)
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }


def get_stock_indicators(db: Session, symbol: str, simulated_date: date = None, 
                        timeframe: str = "1Y", ema_period: int = 20) -> Dict[str, Any]:
    """Get technical indicators for a stock"""
    from routers.data import calculate_start_date
    
    # Parse simulated date
    if simulated_date is None:
        # Use latest available date
        latest_data = db.query(StockData).filter(
            StockData.symbol == symbol.upper()
        ).order_by(StockData.date.desc()).first()
        
        if latest_data:
            simulated_date = latest_data.date
        else:
            return {"error": f"No data found for symbol {symbol}"}
    
    # Calculate start date based on timeframe
    start_date = calculate_start_date(simulated_date, timeframe)
    
    # Get stock data
    stock_data = db.query(StockData).filter(
        StockData.symbol == symbol.upper(),
        StockData.date >= start_date,
        StockData.date <= simulated_date
    ).order_by(StockData.date.asc()).all()
    
    if not stock_data:
        return {"error": f"No data found for {symbol} in timeframe {timeframe}"}
    
    # Extract closing prices
    dates = [data.date for data in stock_data]
    close_prices = [float(data.close) for data in stock_data]
    
    # Calculate indicators
    ema_values = calculate_ema(close_prices, ema_period)
    macd_data = calculate_macd(close_prices)
    
    # Combine results
    indicators = []
    for i, data in enumerate(stock_data):
        indicators.append({
            "date": data.date,
            "ema": ema_values[i],
            "macd": macd_data['macd'][i],
            "macd_signal": macd_data['signal'][i],
            "macd_histogram": macd_data['histogram'][i]
        })
    
    return {
        "symbol": symbol.upper(),
        "simulated_date": simulated_date,
        "timeframe": timeframe,
        "ema_period": ema_period,
        "indicators": indicators
    }


def get_ema_data(db: Session, symbol: str, period: int = 20, simulated_date: date = None, 
                 timeframe: str = "1Y") -> Dict[str, Any]:
    """Get EMA data for a stock"""
    result = get_stock_indicators(db, symbol, simulated_date, timeframe, period)
    
    if "error" in result:
        return result
    
    # Extract just EMA data
    ema_data = []
    for indicator in result["indicators"]:
        if indicator["ema"] is not None:
            ema_data.append({
                "date": indicator["date"],
                "ema": indicator["ema"]
            })
    
    return {
        "symbol": symbol.upper(),
        "period": period,
        "data": ema_data
    }


def get_macd_data(db: Session, symbol: str, fast_period: int = 12, slow_period: int = 26, 
                  signal_period: int = 9, simulated_date: date = None, timeframe: str = "1Y") -> Dict[str, Any]:
    """Get MACD data for a stock"""
    # Get stock data for calculation
    from routers.data import calculate_start_date
    
    if simulated_date is None:
        latest_data = db.query(StockData).filter(
            StockData.symbol == symbol.upper()
        ).order_by(StockData.date.desc()).first()
        
        if latest_data:
            simulated_date = latest_data.date
        else:
            return {"error": f"No data found for symbol {symbol}"}
    
    start_date = calculate_start_date(simulated_date, timeframe)
    
    stock_data = db.query(StockData).filter(
        StockData.symbol == symbol.upper(),
        StockData.date >= start_date,
        StockData.date <= simulated_date
    ).order_by(StockData.date.asc()).all()
    
    if not stock_data:
        return {"error": f"No data found for {symbol} in timeframe {timeframe}"}
    
    # Calculate MACD
    close_prices = [float(data.close) for data in stock_data]
    macd_data = calculate_macd(close_prices, fast_period, slow_period, signal_period)
    
    # Combine results
    macd_results = []
    for i, data in enumerate(stock_data):
        if macd_data['macd'][i] is not None:
            macd_results.append({
                "date": data.date,
                "macd": macd_data['macd'][i],
                "signal": macd_data['signal'][i],
                "histogram": macd_data['histogram'][i]
            })
    
    return {
        "symbol": symbol.upper(),
        "fast_period": fast_period,
        "slow_period": slow_period,
        "signal_period": signal_period,
        "data": macd_results
    }


def get_sma_data(db: Session, symbol: str, period: int = 20, simulated_date: date = None, 
                 timeframe: str = "1Y") -> Dict[str, Any]:
    """Get SMA data for a stock"""
    from routers.data import calculate_start_date
    
    if simulated_date is None:
        latest_data = db.query(StockData).filter(
            StockData.symbol == symbol.upper()
        ).order_by(StockData.date.desc()).first()
        
        if latest_data:
            simulated_date = latest_data.date
        else:
            return {"error": f"No data found for symbol {symbol}"}
    
    start_date = calculate_start_date(simulated_date, timeframe)
    
    stock_data = db.query(StockData).filter(
        StockData.symbol == symbol.upper(),
        StockData.date >= start_date,
        StockData.date <= simulated_date
    ).order_by(StockData.date.asc()).all()
    
    if not stock_data:
        return {"error": f"No data found for {symbol} in timeframe {timeframe}"}
    
    # Calculate SMA
    close_prices = [float(data.close) for data in stock_data]
    sma_values = calculate_sma(close_prices, period)
    
    # Extract SMA data - keep all dates, return null for unavailable values
    sma_data = []
    for i, data in enumerate(stock_data):
        sma_value = sma_values[i]
        # Only include points where SMA can actually be calculated (not NaN)
        if sma_value is not None and not pd.isna(sma_value):
            sma_data.append({
                "date": data.date,
                "ema": float(sma_value)  # Using 'ema' field for consistency with frontend
            })
    
    return {
        "symbol": symbol.upper(),
        "period": period,
        "data": sma_data
    }


def get_rsi_data(db: Session, symbol: str, period: int = 14, simulated_date: date = None, 
                 timeframe: str = "1Y") -> Dict[str, Any]:
    """Get RSI data for a stock"""
    from routers.data import calculate_start_date
    
    if simulated_date is None:
        latest_data = db.query(StockData).filter(
            StockData.symbol == symbol.upper()
        ).order_by(StockData.date.desc()).first()
        
        if latest_data:
            simulated_date = latest_data.date
        else:
            return {"error": f"No data found for symbol {symbol}"}
    
    start_date = calculate_start_date(simulated_date, timeframe)
    
    stock_data = db.query(StockData).filter(
        StockData.symbol == symbol.upper(),
        StockData.date >= start_date,
        StockData.date <= simulated_date
    ).order_by(StockData.date.asc()).all()
    
    if not stock_data:
        return {"error": f"No data found for {symbol} in timeframe {timeframe}"}
    
    # Calculate RSI
    close_prices = [float(data.close) for data in stock_data]
    rsi_values = calculate_rsi(close_prices, period)
    
    # Extract RSI data (scale to price range for display on price chart)
    rsi_data = []
    if close_prices:
        price_min, price_max = min(close_prices), max(close_prices)
        price_range = price_max - price_min
        
        for i, data in enumerate(stock_data):
            rsi_value = rsi_values[i]
            # Only include points where RSI can actually be calculated (not None or NaN)
            if rsi_value is not None and not pd.isna(rsi_value):
                # Scale RSI (0-100) to price range for overlay display
                scaled_rsi = price_min + (rsi_value / 100.0) * price_range
                rsi_data.append({
                    "date": data.date,
                    "rsi": rsi_value  # Use actual RSI value, not scaled
                })
    
    return {
        "symbol": symbol.upper(),
        "period": period,
        "data": rsi_data
    }


def get_obv_data(db: Session, symbol: str, simulated_date: date = None, 
                 timeframe: str = "1Y") -> Dict[str, Any]:
    """Get OBV data for a stock"""
    from routers.data import calculate_start_date
    
    if simulated_date is None:
        latest_data = db.query(StockData).filter(
            StockData.symbol == symbol.upper()
        ).order_by(StockData.date.desc()).first()
        
        if latest_data:
            simulated_date = latest_data.date
        else:
            return {"error": f"No data found for symbol {symbol}"}
    
    start_date = calculate_start_date(simulated_date, timeframe)
    
    stock_data = db.query(StockData).filter(
        StockData.symbol == symbol.upper(),
        StockData.date >= start_date,
        StockData.date <= simulated_date
    ).order_by(StockData.date.asc()).all()
    
    if not stock_data:
        return {"error": f"No data found for {symbol} in timeframe {timeframe}"}
    
    # Calculate OBV
    close_prices = [float(data.close) for data in stock_data]
    volumes = [float(data.volume) for data in stock_data]
    obv_values = calculate_obv(close_prices, volumes)
    
    # Extract OBV data (scale to price range for display on price chart)
    obv_data = []
    if close_prices and obv_values:
        price_min, price_max = min(close_prices), max(close_prices)
        price_range = price_max - price_min
        # Filter out None and NaN values for range calculation
        obv_filtered = [x for x in obv_values if x is not None and not pd.isna(x)]
        
        if obv_filtered:
            obv_min, obv_max = min(obv_filtered), max(obv_filtered)
            obv_range = obv_max - obv_min if obv_max != obv_min else 1
            
            for i, data in enumerate(stock_data):
                obv_value = obv_values[i]
                # Only include points where OBV can actually be calculated (not None or NaN)
                if obv_value is not None and not pd.isna(obv_value):
                    # Scale OBV to price range for overlay display
                    scaled_obv = price_min + ((obv_value - obv_min) / obv_range) * price_range
                    obv_data.append({
                        "date": data.date,
                        "obv": obv_value  # Use actual OBV value
                    })
    
    return {
        "symbol": symbol.upper(),
        "data": obv_data
    }


def get_vpt_data(db: Session, symbol: str, simulated_date: date = None, 
                 timeframe: str = "1Y") -> Dict[str, Any]:
    """Get VPT data for a stock"""
    from routers.data import calculate_start_date
    
    if simulated_date is None:
        latest_data = db.query(StockData).filter(
            StockData.symbol == symbol.upper()
        ).order_by(StockData.date.desc()).first()
        
        if latest_data:
            simulated_date = latest_data.date
        else:
            return {"error": f"No data found for symbol {symbol}"}
    
    start_date = calculate_start_date(simulated_date, timeframe)
    
    stock_data = db.query(StockData).filter(
        StockData.symbol == symbol.upper(),
        StockData.date >= start_date,
        StockData.date <= simulated_date
    ).order_by(StockData.date.asc()).all()
    
    if not stock_data:
        return {"error": f"No data found for {symbol} in timeframe {timeframe}"}
    
    # Calculate VPT
    close_prices = [float(data.close) for data in stock_data]
    volumes = [float(data.volume) for data in stock_data]
    vpt_values = calculate_vpt(close_prices, volumes)
    
    # Extract VPT data (scale to price range for display on price chart)
    vpt_data = []
    if close_prices and vpt_values:
        price_min, price_max = min(close_prices), max(close_prices)
        price_range = price_max - price_min
        # Filter out None and NaN values for range calculation
        vpt_filtered = [x for x in vpt_values if x is not None and not pd.isna(x)]
        
        if vpt_filtered:
            vpt_min, vpt_max = min(vpt_filtered), max(vpt_filtered)
            vpt_range = vpt_max - vpt_min if vpt_max != vpt_min else 1
            
            for i, data in enumerate(stock_data):
                vpt_value = vpt_values[i]
                # Only include points where VPT can actually be calculated (not None or NaN)
                if vpt_value is not None and not pd.isna(vpt_value):
                    # Scale VPT to price range for overlay display
                    scaled_vpt = price_min + ((vpt_value - vpt_min) / vpt_range) * price_range
                    vpt_data.append({
                        "date": data.date,
                        "vpt": vpt_value  # Use actual VPT value
                    })
    
    return {
        "symbol": symbol.upper(),
        "data": vpt_data
    }


def get_vix_data(db: Session, symbol: str, period: int = 20, simulated_date: date = None, 
                 timeframe: str = "1Y") -> Dict[str, Any]:
    """Get VIX-like volatility data for a stock"""
    from routers.data import calculate_start_date
    
    if simulated_date is None:
        latest_data = db.query(StockData).filter(
            StockData.symbol == symbol.upper()
        ).order_by(StockData.date.desc()).first()
        
        if latest_data:
            simulated_date = latest_data.date
        else:
            return {"error": f"No data found for symbol {symbol}"}
    
    start_date = calculate_start_date(simulated_date, timeframe)
    
    stock_data = db.query(StockData).filter(
        StockData.symbol == symbol.upper(),
        StockData.date >= start_date,
        StockData.date <= simulated_date
    ).order_by(StockData.date.asc()).all()
    
    if not stock_data:
        return {"error": f"No data found for {symbol} in timeframe {timeframe}"}
    
    # Calculate volatility (VIX-like)
    close_prices = [float(data.close) for data in stock_data]
    vix_values = calculate_volatility(close_prices, period)
    
    # Extract VIX data (scale to price range for display on price chart)
    vix_data = []
    if close_prices:
        price_min, price_max = min(close_prices), max(close_prices)
        price_range = price_max - price_min
        # Filter out None and NaN values for range calculation
        vix_filtered = [x for x in vix_values if x is not None and not pd.isna(x)]
        
        if vix_filtered:
            vix_min, vix_max = min(vix_filtered), max(vix_filtered)
            vix_range = vix_max - vix_min if vix_max != vix_min else 1
            
            for i, data in enumerate(stock_data):
                vix_value = vix_values[i]
                # Only include points where VIX can actually be calculated (not None or NaN)
                if vix_value is not None and not pd.isna(vix_value):
                    # Scale VIX to price range for overlay display
                    scaled_vix = price_min + ((vix_value - vix_min) / vix_range) * price_range
                    vix_data.append({
                        "date": data.date,
                        "volatility": vix_value  # Use actual volatility value
                    })
    
    return {
        "symbol": symbol.upper(),
        "period": period,
        "data": vix_data
    }