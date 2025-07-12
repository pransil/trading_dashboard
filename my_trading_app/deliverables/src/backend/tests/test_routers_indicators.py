"""
Tests for indicators router
"""
import pytest


class TestIndicatorsRouter:
    """Test the indicators router endpoints"""
    
    def test_get_ema_success(self, db_session, client, sample_stock_data):
        """Test getting EMA data successfully"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/indicators/TSLA/ema?period=2")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert data["period"] == 2
        assert "data" in data
        assert len(data["data"]) >= 1
    
    def test_get_ema_with_timeframe(self, db_session, client, sample_stock_data):
        """Test getting EMA data with specific timeframe"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/indicators/TSLA/ema?period=2&timeframe=1M")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert data["period"] == 2
    
    def test_get_ema_with_simulated_date(self, db_session, client, sample_stock_data):
        """Test getting EMA data with simulated date"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/indicators/TSLA/ema?period=2&simulated_date=2023-01-02")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "TSLA"
        # Should only include data up to the simulated date
        for point in data["data"]:
            assert point["date"] <= "2023-01-02"
    
    def test_get_ema_invalid_symbol(self, db_session, client):
        """Test getting EMA data for invalid symbol"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/indicators/INVALID/ema")
        assert response.status_code == 404
        assert "No data found" in response.json()["detail"]
    
    def test_get_ema_invalid_date_format(self, client, sample_stock_data):
        """Test getting EMA data with invalid date format"""
        response = client.get("/api/indicators/TSLA/ema?simulated_date=invalid-date")
        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]
    
    def test_get_sma_success(self, db_session, client, sample_stock_data):
        """Test getting SMA data successfully"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/indicators/TSLA/sma?period=2")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert data["period"] == 2
        assert "data" in data
    
    def test_get_rsi_success(self, db_session, client, sample_stock_data):
        """Test getting RSI data successfully"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/indicators/TSLA/rsi?period=2")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert data["period"] == 2
        assert "data" in data
    
    def test_get_obv_success(self, db_session, client, sample_stock_data):
        """Test getting OBV data successfully"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/indicators/TSLA/obv")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert "data" in data
    
    def test_get_vpt_success(self, db_session, client, sample_stock_data):
        """Test getting VPT data successfully"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/indicators/TSLA/vpt")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert "data" in data
    
    def test_get_vix_success(self, db_session, client, sample_stock_data):
        """Test getting VIX data successfully"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/indicators/TSLA/vix?period=2")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert data["period"] == 2
        assert "data" in data
    
    def test_get_macd_success(self, db_session, client, sample_stock_data):
        """Test getting MACD data successfully"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/indicators/TSLA/macd?fast_period=2&slow_period=3&signal_period=2")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert data["fast_period"] == 2
        assert data["slow_period"] == 3
        assert data["signal_period"] == 2
        assert "data" in data
    
    def test_get_all_indicators_not_implemented(self, client, sample_stock_data):
        """Test that get all indicators returns 501 (not implemented)"""
        response = client.get("/api/indicators/TSLA/all")
        assert response.status_code == 501
        assert "not implemented" in response.json()["detail"]
    
    def test_case_insensitive_symbol(self, db_session, client, sample_stock_data):
        """Test that symbol lookup is case insensitive"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/indicators/tsla/ema?period=2")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "TSLA"  # Should be uppercase
    
    def test_default_parameters(self, db_session, client, sample_stock_data):
        """Test default parameter values"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        # Test EMA with default period
        response = client.get("/api/indicators/TSLA/ema")
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == 20  # Default EMA period
        
        # Test RSI with default period
        response = client.get("/api/indicators/TSLA/rsi")
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == 14  # Default RSI period
        
        # Test MACD with default periods
        response = client.get("/api/indicators/TSLA/macd")
        assert response.status_code == 200
        data = response.json()
        assert data["fast_period"] == 12
        assert data["slow_period"] == 26
        assert data["signal_period"] == 9