"""
Tests for stocks router
"""
import pytest
from decimal import Decimal


class TestStocksRouter:
    """Test the stocks router endpoints"""
    
    def test_get_stocks_empty(self, db_session, client):
        """Test getting stocks when database is empty"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/stocks/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_stocks_with_data(self, db_session, client, multiple_stocks_data):
        """Test getting stocks with data"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        stocks, _ = multiple_stocks_data
        
        response = client.get("/api/stocks/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        
        symbols = [stock["symbol"] for stock in data]
        assert "AAPL" in symbols
        assert "GOOGL" in symbols
        assert "MSFT" in symbols
    
    def test_get_stocks_count_empty(self, db_session, client):
        """Test getting stock count when database is empty"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/stocks/count")
        assert response.status_code == 200
        assert response.json() == {"count": 0}
    
    def test_get_stocks_count_with_data(self, db_session, client, multiple_stocks_data):
        """Test getting stock count with data"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/stocks/count")
        assert response.status_code == 200
        assert response.json() == {"count": 3}
    
    def test_get_date_range_no_symbol(self, db_session, client, multiple_stocks_data):
        """Test getting date range for all stocks"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/stocks/date-range")
        assert response.status_code == 200
        
        data = response.json()
        assert "min_date" in data
        assert "max_date" in data
        assert data["min_date"] == "2023-01-01"
        assert data["max_date"] == "2023-01-05"
    
    def test_get_date_range_specific_symbol(self, db_session, client, sample_stock_data):
        """Test getting date range for specific symbol"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/stocks/date-range?symbol=TSLA")
        assert response.status_code == 200
        
        data = response.json()
        assert data["min_date"] == "2023-01-01"
        assert data["max_date"] == "2023-01-03"
    
    def test_get_stock_details_success(self, db_session, client, sample_stock_data):
        """Test getting stock details successfully"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/stocks/TSLA/details")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert data["current_price"] == "108.00"  # Latest price
        assert data["change"] == "2.00"  # 108 - 106
        assert float(data["change_percent"]) == pytest.approx(1.887, rel=1e-2)
        assert data["volume"] == 1100000
    
    def test_get_stock_details_with_simulated_date(self, db_session, client, sample_stock_data):
        """Test getting stock details with simulated date"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/stocks/TSLA/details?simulated_date=2023-01-02")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert data["current_price"] == "106.00"  # Price on 2023-01-02
        assert data["change"] == "4.00"  # 106 - 102
        assert float(data["change_percent"]) == pytest.approx(3.922, rel=1e-2)
    
    def test_get_stock_details_invalid_symbol(self, db_session, client):
        """Test getting stock details for invalid symbol"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/stocks/INVALID/details")
        assert response.status_code == 400  # Invalid symbol returns 400, not 404
        assert "No data found" in response.json()["detail"]
    
    def test_get_stock_details_invalid_date_format(self, db_session, client, sample_stock_data):
        """Test getting stock details with invalid date format"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/stocks/TSLA/details?simulated_date=invalid-date")
        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]
    
    def test_get_stock_details_52_week_range(self, client, db_session, sample_stock):
        """Test 52-week high/low calculation"""
        from tests.conftest import ensure_db_ready
        from models.database import StockData
        from datetime import date
        
        ensure_db_ready(db_session)
        
        # Add data spanning more than a year
        data_points = []
        for month in range(1, 13):  # 12 months
            data_point = StockData(
                symbol="TSLA",
                date=date(2023, month, 15),
                open=Decimal(str(100 + month)),
                high=Decimal(str(105 + month)),  # High increases each month
                low=Decimal(str(95 + month)),    # Low increases each month
                close=Decimal(str(102 + month)),
                adj_close=Decimal(str(102 + month)),
                volume=1000000
            )
            data_points.append(data_point)
            db_session.add(data_point)
        
        db_session.commit()
        
        # Ensure database is ready after adding new data
        ensure_db_ready(db_session)
        
        response = client.get("/api/stocks/TSLA/details")
        assert response.status_code == 200
        
        data = response.json()
        # Highest high should be 105 + 12 = 117
        # Lowest low should be 95 + 1 = 96
        assert data["high_52w"] == "117.00"
        assert data["low_52w"] == "96.00"