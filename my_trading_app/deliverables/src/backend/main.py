from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from routers import stocks, data, indicators, watchlist
from models.database import init_db
from services.data_import import import_all_stocks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Trading Dashboard API...")
    init_db()
    # Import data on startup if needed
    # await import_all_stocks()
    yield
    # Shutdown
    logger.info("Shutting down Trading Dashboard API...")


app = FastAPI(
    title="Trading Dashboard API",
    description="API for historical stock data visualization with technical indicators",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["indicators"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])


@app.get("/")
async def root():
    return {"message": "Trading Dashboard API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}