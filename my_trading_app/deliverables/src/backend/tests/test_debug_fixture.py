#!/usr/bin/env python3
"""Debug pytest fixtures"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_debug_with_fixtures(db_session, sample_stock, sample_stock_data, client):
    """Test with debug output"""
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