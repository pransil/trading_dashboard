"""
Tests for database models
"""
import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from models.database import Stock, StockData


class TestStockModel:
    """Test the Stock model"""
    
    def test_create_stock(self, db_session):
        """Test creating a stock"""
        stock = Stock(symbol="AAPL", name="Apple Inc")
        db_session.add(stock)
        db_session.commit()
        
        assert stock.symbol == "AAPL"
        assert stock.name == "Apple Inc"
    
    def test_stock_symbol_primary_key(self, db_session):
        """Test that symbol is primary key"""
        stock1 = Stock(symbol="AAPL", name="Apple Inc")
        stock2 = Stock(symbol="AAPL", name="Apple Corporation")  # Same symbol
        
        db_session.add(stock1)
        db_session.commit()
        
        db_session.add(stock2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_stock_relationship(self, db_session, sample_stock, sample_stock_data):
        """Test the relationship between Stock and StockData"""
        assert len(sample_stock.data_points) == 3
        assert all(data.symbol == "TSLA" for data in sample_stock.data_points)


class TestStockDataModel:
    """Test the StockData model"""
    
    def test_create_stock_data(self, db_session, sample_stock):
        """Test creating stock data"""
        data = StockData(
            symbol="TSLA",
            date=date(2023, 1, 1),
            open=Decimal("100.00"),
            high=Decimal("105.00"),
            low=Decimal("98.00"),
            close=Decimal("102.00"),
            adj_close=Decimal("102.00"),
            volume=1000000
        )
        db_session.add(data)
        db_session.commit()
        
        assert data.symbol == "TSLA"
        assert data.date == date(2023, 1, 1)
        assert data.open == Decimal("100.00")
        assert data.volume == 1000000
    
    def test_unique_symbol_date_constraint(self, db_session, sample_stock):
        """Test that symbol-date combination must be unique"""
        data1 = StockData(
            symbol="TSLA",
            date=date(2023, 1, 1),
            open=Decimal("100.00"),
            high=Decimal("105.00"),
            low=Decimal("98.00"),
            close=Decimal("102.00"),
            adj_close=Decimal("102.00"),
            volume=1000000
        )
        
        data2 = StockData(
            symbol="TSLA",
            date=date(2023, 1, 1),  # Same date
            open=Decimal("101.00"),
            high=Decimal("106.00"),
            low=Decimal("99.00"),
            close=Decimal("103.00"),
            adj_close=Decimal("103.00"),
            volume=1100000
        )
        
        db_session.add(data1)
        db_session.commit()
        
        db_session.add(data2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_foreign_key_constraint(self, db_session):
        """Test that foreign key constraint works"""
        # Try to add data for non-existent stock
        data = StockData(
            symbol="NONEXISTENT",
            date=date(2023, 1, 1),
            open=Decimal("100.00"),
            high=Decimal("105.00"),
            low=Decimal("98.00"),
            close=Decimal("102.00"),
            adj_close=Decimal("102.00"),
            volume=1000000
        )
        db_session.add(data)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_decimal_precision(self, db_session, sample_stock):
        """Test that decimal values are stored with correct precision"""
        data = StockData(
            symbol="TSLA",
            date=date(2023, 1, 1),
            open=Decimal("123.456"),  # More than 2 decimal places
            high=Decimal("125.789"),
            low=Decimal("121.234"),
            close=Decimal("124.567"),
            adj_close=Decimal("124.567"),
            volume=1000000
        )
        db_session.add(data)
        db_session.commit()
        db_session.refresh(data)
        
        # Check that values are rounded to 2 decimal places
        assert data.open == Decimal("123.46")
        assert data.high == Decimal("125.79")
        assert data.low == Decimal("121.23")
        assert data.close == Decimal("124.57")