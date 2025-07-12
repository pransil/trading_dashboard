"""
Pytest configuration and fixtures for the trading dashboard backend
"""
import pytest
import tempfile
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import date, datetime
from decimal import Decimal

# Import all models to ensure they're registered with Base before creating tables
from models.database import Base, get_db, Stock, StockData
# Import FastAPI components separately to avoid lifespan events
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@pytest.fixture(scope="function")
def db_session():
    """Create a database session for testing with fresh database for each test"""
    # Create in-memory SQLite database for each test with foreign key enforcement
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={
            "check_same_thread": False,
        }
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    # Store engine reference for cleanup
    session._test_engine = engine
    
    yield session
    
    session.close()
    engine.dispose()


@pytest.fixture(scope="function")
def test_app():
    """Create a test FastAPI app without lifespan events"""
    app = FastAPI(
        title="Trading Dashboard API",
        description="API for historical stock data visualization with technical indicators",
        version="1.0.0"
    )

    # Configure CORS for React frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    from routers.stocks import router as stocks_router
    from routers.data import router as data_router
    from routers.indicators import router as indicators_router
    from routers.watchlist import router as watchlist_router
    
    app.include_router(stocks_router, prefix="/api/stocks", tags=["stocks"])
    app.include_router(data_router, prefix="/api/data", tags=["data"])
    app.include_router(indicators_router, prefix="/api/indicators", tags=["indicators"])
    app.include_router(watchlist_router, prefix="/api/watchlist", tags=["watchlist"])

    @app.get("/")
    async def root():
        return {"message": "Trading Dashboard API", "version": "1.0.0"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app


@pytest.fixture(scope="function")
def client(db_session, test_app):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Don't close the session here, let the fixture handle it
    
    test_app.dependency_overrides[get_db] = override_get_db
    
    try:
        with TestClient(test_app) as test_client:
            yield test_client
    finally:
        test_app.dependency_overrides.clear()


@pytest.fixture
def sample_stock(db_session):
    """Create a sample stock for testing"""
    stock = Stock(symbol="TSLA", name="Tesla Inc")
    db_session.add(stock)
    db_session.commit()
    db_session.refresh(stock)
    return stock


@pytest.fixture
def sample_stock_data(db_session, sample_stock):
    """Create sample stock data for testing"""
    data_points = [
        StockData(
            symbol="TSLA",
            date=date(2023, 1, 1),
            open=Decimal("100.00"),
            high=Decimal("105.00"),
            low=Decimal("98.00"),
            close=Decimal("102.00"),
            adj_close=Decimal("102.00"),
            volume=1000000
        ),
        StockData(
            symbol="TSLA",
            date=date(2023, 1, 2),
            open=Decimal("102.00"),
            high=Decimal("108.00"),
            low=Decimal("101.00"),
            close=Decimal("106.00"),
            adj_close=Decimal("106.00"),
            volume=1200000
        ),
        StockData(
            symbol="TSLA",
            date=date(2023, 1, 3),
            open=Decimal("106.00"),
            high=Decimal("110.00"),
            low=Decimal("104.00"),
            close=Decimal("108.00"),
            adj_close=Decimal("108.00"),
            volume=1100000
        )
    ]
    
    for data_point in data_points:
        db_session.add(data_point)
    
    db_session.commit()
    return data_points


@pytest.fixture
def multiple_stocks_data(db_session):
    """Create multiple stocks with data for testing"""
    stocks = [
        Stock(symbol="AAPL", name="Apple Inc"),
        Stock(symbol="GOOGL", name="Alphabet Inc"),
        Stock(symbol="MSFT", name="Microsoft Corp")
    ]
    
    for stock in stocks:
        db_session.add(stock)
    
    # Add some data for each stock
    stock_data = []
    for i, symbol in enumerate(["AAPL", "GOOGL", "MSFT"]):
        base_price = 100 + (i * 50)  # Different price ranges
        for day in range(1, 6):  # 5 days of data
            data_point = StockData(
                symbol=symbol,
                date=date(2023, 1, day),
                open=Decimal(str(base_price + day - 1)),
                high=Decimal(str(base_price + day + 2)),
                low=Decimal(str(base_price + day - 2)),
                close=Decimal(str(base_price + day)),
                adj_close=Decimal(str(base_price + day)),
                volume=1000000 + (i * 100000)
            )
            stock_data.append(data_point)
            db_session.add(data_point)
    
    db_session.commit()
    return stocks, stock_data


def ensure_db_ready(db_session):
    """
    Ensure database session is ready for API tests.
    This function "warms up" the session by accessing the database,
    which resolves timing issues with table creation in tests.
    """
    from models.database import Stock, StockData
    
    # Simple query to ensure session is active and tables are accessible
    try:
        db_session.query(Stock).count()
        db_session.query(StockData).count()
    except Exception:
        # If there's an issue, the test will fail anyway, but this ensures
        # any session setup happens before API calls
        pass