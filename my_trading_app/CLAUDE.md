# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Trading Dashboard application for visualizing historical stock data with technical indicators. Users can select any historical date as "current" to analyze market conditions without future data leakage.

## Technology Stack

- **Frontend**: React 19 with TypeScript, Material-UI 7, Redux Toolkit, lightweight-charts
- **Backend**: Python FastAPI with SQLAlchemy ORM, using SQLite database
- **Charts**: lightweight-charts (TradingView) for candlestick and MACD visualization
- **State Management**: Redux Toolkit for managing selected stock, simulated date, and watchlist
- **API Communication**: Axios for REST API calls

## Essential Commands

### Backend Development
```bash
# Install Python dependencies
cd deliverables
pip install -r requirements.txt

# Run FastAPI development server
cd deliverables/src/backend
uvicorn main:app --reload --port 8000

# Run backend tests
cd deliverables/src/backend
pytest -v

# Run specific test file
pytest tests/test_routers_stocks.py -v

# Run with coverage
pytest --cov=. --cov-report=html

# Code formatting and linting
black .
isort .
flake8 .
mypy .
```

### Frontend Development
```bash
# Install frontend dependencies
cd deliverables/src/frontend
npm install

# Run React development server (port 3000)
npm start

# Build for production
npm run build

# Run frontend tests
npm test

# Run tests in watch mode
npm test -- --watch
```

### Quick Start/Stop Scripts
```bash
# Start both frontend and backend servers with proper cleanup
./scripts/start.sh

# Stop all servers and clean up ports
./scripts/stop.sh
```

### Database Operations
```bash
# Database is SQLite, located at: my_trading_app/trading_dashboard.db
# To import CSV data from Kaggle dataset:
cd my_trading_app
python import_sample_stocks.py  # Import sample stocks
python test_import.py          # Test the import process
```

## High-Level Architecture

### API Endpoints Structure
- `/api/stocks` - Stock management (list, search, details)
- `/api/data` - Historical price data with simulated date filtering
- `/api/indicators` - Technical indicators (EMA, MACD) calculations
- `/api/watchlist` - User watchlist management

### Key Backend Components
- **models/database.py**: SQLAlchemy models for Stock and StockData tables with SQLite
- **routers/**: FastAPI route handlers for each API endpoint group
- **services/**: Business logic for data import, indicator calculations, stock operations
- **services/indicator_calc.py**: EMA and MACD calculation implementations

### Frontend Architecture
- **SimpleTradingDashboard.tsx**: Main dashboard component managing all state and panels
- **CandlestickChart.tsx**: Price chart with EMA overlay using lightweight-charts
- **MACDChart.tsx**: MACD indicator chart synchronized with main chart
- **IndicatorPanel.tsx**: Stock details display (price, change, volume, 52W range)

### Data Flow
1. CSV files → import_sample_stocks.py → SQLite database
2. Frontend date selection → API filters data → Returns only data up to simulated date
3. Indicator calculations happen server-side to ensure consistency
4. Charts receive filtered data ensuring no future information leakage

## Critical Implementation Details

### Simulated Date Handling
- All API endpoints accept `simulated_date` parameter
- Backend filters ensure no data after simulated date is returned
- Frontend prevents selecting future dates beyond available data

### Database Indexes
- Composite index on (symbol, date) for efficient queries
- Unique constraint ensures no duplicate entries per symbol/date

### CORS Configuration
- Backend configured to accept requests from localhost:3000 (React dev server)
- Update CORS settings in main.py for production deployment

### Testing Approach
- Backend: pytest with async support for FastAPI endpoints
- Mock database fixtures in conftest.py for isolated testing
- Frontend: React Testing Library for component tests

## Common Development Tasks

### Adding New Technical Indicators
1. Add calculation logic to services/indicator_calc.py
2. Create new endpoint in routers/indicators.py
3. Add frontend API call in SimpleTradingDashboard.tsx
4. Create/update chart component to display indicator

### Importing Additional Stock Data
1. Place CSV files in `/Users/patransil/dev/prediction/kaggle_stock_data`
2. Run import script or modify import_sample_stocks.py
3. Verify data with test_import.py

### Modifying Chart Behavior
1. Charts use lightweight-charts library (TradingView)
2. Chart components in frontend/src/components/
3. Synchronization logic in SimpleTradingDashboard.tsx handleChartCrosshairMove