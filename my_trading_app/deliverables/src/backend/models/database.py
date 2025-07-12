from sqlalchemy import create_engine, Column, String, Date, Numeric, BigInteger, Index, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os
from pathlib import Path

# Get the absolute path to the database
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
DATABASE_PATH = BASE_DIR / "trading_dashboard.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Stock(Base):
    __tablename__ = "stocks"
    
    symbol = Column(String(10), primary_key=True)
    name = Column(String(255))
    
    # Relationship
    data_points = relationship("StockData", back_populates="stock", cascade="all, delete-orphan")


class StockData(Base):
    __tablename__ = "stock_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), ForeignKey("stocks.symbol"), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    adj_close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    
    # Relationship
    stock = relationship("Stock", back_populates="data_points")
    
    # Indexes
    __table_args__ = (
        Index("idx_stock_data_symbol_date", "symbol", "date"),
        Index("idx_stock_data_date", "date"),
        # Ensure unique symbol-date combination
        Index("idx_stock_data_unique", "symbol", "date", unique=True),
    )


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()