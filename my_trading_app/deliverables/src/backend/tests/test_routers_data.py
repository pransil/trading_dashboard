"""
Tests for data router
"""
import pytest
from datetime import date, timedelta

from routers.data import calculate_start_date


class TestDataRouter:
    """Test the data router endpoints"""
    
    def test_get_stock_data_success(self, db_session, sample_stock, sample_stock_data, client):
        """Test getting stock data successfully"""
        from models.database import Stock, StockData
        
        # Verify database state first (this seems to "warm up" the session)
        stock_count = db_session.query(Stock).count()
        data_count = db_session.query(StockData).count()
        assert stock_count == 1
        assert data_count == 3
        
        response = client.get("/api/data/TSLA")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert len(data["data"]) == 3
        
        # Check that data is sorted by date ascending
        dates = [item["date"] for item in data["data"]]
        assert dates == ["2023-01-01", "2023-01-02", "2023-01-03"]
    
    def test_get_stock_data_with_simulated_date(self, db_session, client, sample_stock_data):
        """Test getting stock data with simulated date"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/data/TSLA?simulated_date=2023-01-02")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["data"]) == 2  # Only data up to 2023-01-02
        
        dates = [item["date"] for item in data["data"]]
        assert dates == ["2023-01-01", "2023-01-02"]
    
    def test_get_stock_data_with_timeframe(self, client, db_session, sample_stock):
        """Test getting stock data with different timeframes"""
        from tests.conftest import ensure_db_ready
        from models.database import StockData
        from decimal import Decimal
        
        ensure_db_ready(db_session)
        
        # Add more data points spanning multiple months
        base_date = date(2023, 1, 1)
        for days in range(0, 100, 7):  # Weekly data for ~3 months
            data_point = StockData(
                symbol="TSLA",
                date=base_date + timedelta(days=days),
                open=Decimal("100.00"),
                high=Decimal("105.00"),
                low=Decimal("98.00"),
                close=Decimal("102.00"),
                adj_close=Decimal("102.00"),
                volume=1000000
            )
            db_session.add(data_point)
        
        db_session.commit()
        
        # Ensure database is ready after adding new data
        ensure_db_ready(db_session)
        
        # Test 1 week timeframe
        response = client.get("/api/data/TSLA?timeframe=1W&simulated_date=2023-04-01")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 2  # Should have limited data
        
        # Test 3 month timeframe
        response = client.get("/api/data/TSLA?timeframe=3M&simulated_date=2023-04-01")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) > 5  # Should have more data
    
    def test_get_stock_data_invalid_symbol(self, db_session, client):
        """Test getting stock data for invalid symbol"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/data/INVALID")
        assert response.status_code == 404
        assert "No data found" in response.json()["detail"]
    
    def test_get_stock_data_invalid_date_format(self, client, sample_stock_data):
        """Test getting stock data with invalid date format"""
        response = client.get("/api/data/TSLA?simulated_date=invalid-date")
        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]
    
    def test_get_stock_data_case_insensitive(self, db_session, client, sample_stock_data):
        """Test that symbol lookup is case insensitive"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        response = client.get("/api/data/tsla")  # lowercase
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "TSLA"  # Should be uppercase in response
    
    def test_get_stock_data_no_data_in_timeframe(self, db_session, client, sample_stock_data):
        """Test getting stock data when no data exists in timeframe"""
        from tests.conftest import ensure_db_ready
        ensure_db_ready(db_session)
        
        # Request data from much earlier date
        response = client.get("/api/data/TSLA?simulated_date=2022-01-01")
        assert response.status_code == 404
        assert "No data found" in response.json()["detail"]


class TestCalculateStartDate:
    """Test the calculate_start_date utility function"""
    
    def test_calculate_start_date_1w(self):
        """Test 1 week timeframe"""
        sim_date = date(2023, 1, 15)
        start_date = calculate_start_date(sim_date, "1W")
        expected = sim_date - timedelta(weeks=1)
        assert start_date == expected
    
    def test_calculate_start_date_1m(self):
        """Test 1 month timeframe"""
        sim_date = date(2023, 2, 15)
        start_date = calculate_start_date(sim_date, "1M")
        expected = sim_date - timedelta(days=30)
        assert start_date == expected
    
    def test_calculate_start_date_3m(self):
        """Test 3 month timeframe"""
        sim_date = date(2023, 4, 15)
        start_date = calculate_start_date(sim_date, "3M")
        expected = sim_date - timedelta(days=90)
        assert start_date == expected
    
    def test_calculate_start_date_6m(self):
        """Test 6 month timeframe"""
        sim_date = date(2023, 7, 15)
        start_date = calculate_start_date(sim_date, "6M")
        expected = sim_date - timedelta(days=180)
        assert start_date == expected
    
    def test_calculate_start_date_1y(self):
        """Test 1 year timeframe"""
        sim_date = date(2023, 12, 15)
        start_date = calculate_start_date(sim_date, "1Y")
        expected = sim_date - timedelta(days=365)
        assert start_date == expected
    
    def test_calculate_start_date_ytd(self):
        """Test year-to-date timeframe"""
        sim_date = date(2023, 6, 15)
        start_date = calculate_start_date(sim_date, "YTD")
        expected = date(2023, 1, 1)
        assert start_date == expected
    
    def test_calculate_start_date_5y(self):
        """Test 5 year timeframe"""
        sim_date = date(2023, 1, 15)
        start_date = calculate_start_date(sim_date, "5Y")
        expected = sim_date - timedelta(days=1825)
        assert start_date == expected
    
    def test_calculate_start_date_invalid_timeframe(self):
        """Test invalid timeframe defaults to 1 year"""
        sim_date = date(2023, 1, 15)
        start_date = calculate_start_date(sim_date, "INVALID")
        expected = sim_date - timedelta(days=365)
        assert start_date == expected


def test_copy_of_working_debug(db_session, sample_stock, sample_stock_data, client):
    """Copy of the working debug test"""
    from models.database import Stock, StockData
    
    # Check what's in the database
    stock_count = db_session.query(Stock).count()
    data_count = db_session.query(StockData).count()
    print(f"\nDatabase has {stock_count} stocks and {data_count} data points")
    
    # Check actual data
    stocks = db_session.query(Stock).all()
    for stock in stocks:
        print(f"Stock: {stock.symbol} - {stock.name}")
    
    data_points = db_session.query(StockData).all()
    for data_point in data_points:
        print(f"Data: {data_point.symbol} {data_point.date} ${data_point.close}")
    
    # Try API call
    response = client.get("/api/data/TSLA")
    print(f"\nAPI Response: {response.status_code}")
    print(f"Response Text: {response.text}")
    
    assert response.status_code == 200