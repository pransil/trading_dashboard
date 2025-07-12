"""
Tests for indicator calculation services
"""
import pytest
import numpy as np
import math
from decimal import Decimal

from services.indicator_calc import (
    calculate_ema, calculate_sma, calculate_rsi, calculate_volatility,
    calculate_obv, calculate_vpt, calculate_macd
)


class TestIndicatorCalculations:
    """Test indicator calculation functions"""
    
    def test_calculate_sma_basic(self):
        """Test basic SMA calculation"""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        period = 3
        
        result = calculate_sma(data, period)
        
        # First 2 values should be NaN (not enough data)
        assert math.isnan(result[0])
        assert math.isnan(result[1])
        
        # SMA values
        assert result[2] == pytest.approx(2.0, rel=1e-6)  # (1+2+3)/3
        assert result[3] == pytest.approx(3.0, rel=1e-6)  # (2+3+4)/3
        assert result[4] == pytest.approx(4.0, rel=1e-6)  # (3+4+5)/3
    
    def test_calculate_sma_insufficient_data(self):
        """Test SMA with insufficient data"""
        data = [1.0, 2.0]
        period = 5
        
        result = calculate_sma(data, period)
        
        assert len(result) == 2
        assert all(x is None for x in result)
    
    def test_calculate_ema_basic(self):
        """Test basic EMA calculation"""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        period = 3
        
        result = calculate_ema(data, period)
        
        # First 2 values should be None (EMA function returns None for insufficient data)
        assert result[0] is None
        assert result[1] is None
        
        # EMA values should be calculated
        assert result[2] is not None
        assert result[3] is not None
        assert result[4] is not None
        
        # EMA should be more responsive than SMA
        assert len(result) == 5
    
    def test_calculate_rsi_basic(self):
        """Test basic RSI calculation"""
        # Create data with clear upward trend
        data = [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0,
                110.0, 111.0, 112.0, 113.0, 114.0, 115.0]
        period = 14
        
        result = calculate_rsi(data, period)
        
        # RSI calculation needs period data points, so first period-1 values should be NaN
        for i in range(period - 1):
            assert math.isnan(result[i])
        
        # RSI should be calculated from index period-1 onward (13, 14, 15)
        assert not math.isnan(result[period - 1])
        assert 0 <= result[period - 1] <= 100
        
        # With consistent upward trend, RSI should be high
        assert result[period - 1] > 50
    
    def test_calculate_volatility_basic(self):
        """Test basic volatility calculation"""
        # Data with varying volatility
        data = [100.0, 102.0, 98.0, 105.0, 97.0, 103.0, 99.0, 104.0, 96.0, 106.0,
                95.0, 107.0, 94.0, 108.0, 93.0, 109.0, 92.0, 110.0, 91.0, 111.0, 90.0]
        period = 20
        
        result = calculate_volatility(data, period)
        
        # First 20 values should be NaN
        for i in range(20):
            assert math.isnan(result[i])
        
        # Volatility should be calculated for last value
        assert not math.isnan(result[20])
        assert result[20] > 0  # Volatility should be positive
    
    def test_calculate_obv_basic(self):
        """Test basic OBV calculation"""
        close_prices = [100.0, 102.0, 101.0, 103.0, 102.0]
        volumes = [1000.0, 1200.0, 800.0, 1500.0, 900.0]
        
        result = calculate_obv(close_prices, volumes)
        
        assert len(result) == 5
        assert result[0] == 0  # Starting value
        
        # Price went up, so add volume
        assert result[1] == 1200.0  # 0 + 1200
        
        # Price went down, so subtract volume
        assert result[2] == 400.0  # 1200 - 800
        
        # Price went up, so add volume
        assert result[3] == 1900.0  # 400 + 1500
        
        # Price went down, so subtract volume
        assert result[4] == 1000.0  # 1900 - 900
    
    def test_calculate_obv_mismatched_lengths(self):
        """Test OBV with mismatched input lengths"""
        close_prices = [100.0, 102.0, 101.0]
        volumes = [1000.0, 1200.0]  # One less than prices
        
        result = calculate_obv(close_prices, volumes)
        
        # Should return None values when lengths don't match
        assert all(x is None for x in result)
    
    def test_calculate_vpt_basic(self):
        """Test basic VPT calculation"""
        close_prices = [100.0, 102.0, 101.0, 103.0]
        volumes = [1000.0, 1200.0, 800.0, 1500.0]
        
        result = calculate_vpt(close_prices, volumes)
        
        assert len(result) == 4
        assert result[0] == 0  # Starting value
        
        # Check calculation: VPT[i] = VPT[i-1] + volume[i] * (price[i] - price[i-1]) / price[i-1]
        price_change_pct_1 = (102.0 - 100.0) / 100.0  # 0.02
        expected_1 = 0 + 1200.0 * price_change_pct_1
        assert result[1] == pytest.approx(expected_1, rel=1e-6)
    
    def test_calculate_macd_basic(self):
        """Test basic MACD calculation"""
        # Create enough data for MACD calculation
        data = list(range(100, 150))  # 50 data points with upward trend
        
        result = calculate_macd(data, fast_period=12, slow_period=26, signal_period=9)
        
        assert "macd" in result
        assert "signal" in result
        assert "histogram" in result
        
        assert len(result["macd"]) == len(data)
        assert len(result["signal"]) == len(data)
        assert len(result["histogram"]) == len(data)
        
        # With upward trend, MACD should eventually be positive
        non_none_macd = [x for x in result["macd"] if x is not None]
        assert len(non_none_macd) > 0
        assert non_none_macd[-1] > 0  # Last value should be positive with upward trend
    
    def test_calculate_macd_insufficient_data(self):
        """Test MACD with insufficient data"""
        data = [100.0, 101.0, 102.0]  # Too little data
        
        result = calculate_macd(data, fast_period=12, slow_period=26, signal_period=9)
        
        # All values should be None
        assert all(x is None for x in result["macd"])
        assert all(x is None for x in result["signal"])
        assert all(x is None for x in result["histogram"])


class TestIndicatorDataFunctions:
    """Test the get_*_data functions"""
    
    def test_get_ema_data_success(self, db_session, sample_stock_data):
        """Test getting EMA data successfully"""
        from services.indicator_calc import get_ema_data
        
        result = get_ema_data(db_session, "TSLA", period=2, timeframe="1Y")
        
        assert "symbol" in result
        assert "period" in result
        assert "data" in result
        assert result["symbol"] == "TSLA"
        assert result["period"] == 2
        assert len(result["data"]) >= 1  # Should have some data points
    
    def test_get_sma_data_success(self, db_session, sample_stock_data):
        """Test getting SMA data successfully"""
        from services.indicator_calc import get_sma_data
        
        result = get_sma_data(db_session, "TSLA", period=2, timeframe="1Y")
        
        assert result["symbol"] == "TSLA"
        assert result["period"] == 2
        assert len(result["data"]) >= 1
    
    def test_get_rsi_data_success(self, db_session, sample_stock_data):
        """Test getting RSI data successfully"""
        from services.indicator_calc import get_rsi_data
        
        result = get_rsi_data(db_session, "TSLA", period=2, timeframe="1Y")
        
        assert result["symbol"] == "TSLA"
        assert result["period"] == 2
        # RSI data is scaled to price range
        assert "data" in result
    
    def test_get_indicator_data_invalid_symbol(self, db_session):
        """Test getting indicator data for invalid symbol"""
        from services.indicator_calc import get_ema_data
        
        result = get_ema_data(db_session, "INVALID", period=20, timeframe="1Y")
        
        assert "error" in result
        assert "No data found" in result["error"]