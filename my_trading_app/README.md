# Trading Dashboard

A web-based trading dashboard for visualizing historical stock data with technical indicators. Users can analyze stock performance by selecting any historical date as the "current" date, preventing future data leakage during backtesting.

## Features

- 📊 **Candlestick Charts** - OHLC data visualization with volume bars
- 📈 **Technical Indicators** - EMA, SMA, MACD, RSI, VIX, OBV, VPT indicators
- 📅 **Time Travel** - Select any historical date as "current" for backtesting
- 📋 **Watchlist** - Monitor multiple stocks with real-time metrics
- 🔍 **Stock Search** - Quick search and selection from available stocks
- ⏰ **Multiple Timeframes** - 1W, 1M, 3M, 6M, 1Y, YTD, 5Y views
- 🔄 **Synchronized Charts** - Price and MACD charts move together

## Tech Stack

- **Frontend**: React 19 with TypeScript, Material-UI, Redux Toolkit
- **Backend**: Python FastAPI with SQLAlchemy ORM
- **Database**: SQLite
- **Charts**: lightweight-charts (TradingView library)

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

## Quick Start

### 1. Clone and setup
```bash
git clone <repository-url>
cd my_trading_app
```

### 2. Install dependencies
```bash
# Backend dependencies
cd deliverables
pip install -r requirements.txt

# Frontend dependencies
cd src/frontend
npm install
cd ../../..
```

### 3. Import sample data
```bash
# Import sample stocks (AAPL, TSLA, NVDA, MSFT, GOOGL)
python import_sample_stocks.py
```

### 4. Start the servers

**Option A - Quick Start (Recommended):**
```bash
./scripts/start.sh
```

**Option B - Manual Start:**

**Backend (Terminal 1):**
```bash
cd deliverables/src/backend
uvicorn main:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd deliverables/src/frontend
npm start
```

**Stop all servers:**
```bash
./scripts/stop.sh
```

The application will be available at http://localhost:3000  
API documentation at http://localhost:8000/docs

## API Endpoints

- `GET /api/stocks` - List all available stocks
- `GET /api/data/{symbol}` - Get historical data for a stock
- `GET /api/indicators/{symbol}/ema` - Calculate EMA for a stock
- `GET /api/indicators/{symbol}/sma` - Calculate SMA for a stock  
- `GET /api/indicators/{symbol}/macd` - Calculate MACD for a stock
- `GET /api/indicators/{symbol}/rsi` - Calculate RSI for a stock
- `GET /api/indicators/{symbol}/vix` - Calculate VIX volatility for a stock
- `GET /api/indicators/{symbol}/obv` - Calculate On-Balance Volume for a stock
- `GET /api/indicators/{symbol}/vpt` - Calculate Volume Price Trend for a stock
- `GET /api/watchlist` - Manage user watchlist

All endpoints support `simulated_date` parameter for time travel functionality.

## Development

### Running Tests

**Backend:**
```bash
cd deliverables/src/backend
pytest -v                           # All tests
pytest tests/test_routers_stocks.py -v  # Specific test
pytest --cov=. --cov-report=html    # With coverage
```

**Frontend:**
```bash
cd deliverables/src/frontend
npm test              # Run tests
npm test -- --watch   # Watch mode
```

### Code Quality

**Backend:**
```bash
cd deliverables/src/backend
black .      # Format code
isort .      # Sort imports
flake8 .     # Lint code
mypy .       # Type checking
```

**Frontend:**
```bash
cd deliverables/src/frontend
npm run build    # Build for production
```

## Project Structure

```
my_trading_app/
├── deliverables/
│   ├── src/
│   │   ├── backend/
│   │   │   ├── main.py              # FastAPI application
│   │   │   ├── models/              # Database models
│   │   │   ├── routers/             # API endpoints
│   │   │   ├── services/            # Business logic
│   │   │   └── tests/               # Backend tests
│   │   └── frontend/
│   │       ├── src/components/      # React components
│   │       ├── src/App.tsx          # Main application
│   │       └── package.json         # Frontend dependencies
│   └── requirements.txt             # Backend dependencies
├── import_sample_stocks.py          # Data import script
├── trading_dashboard.db             # SQLite database
└── CLAUDE.md                        # Development guide
```

## Data Format

The application expects CSV files with columns: Date, Open, High, Low, Close, Adj Close, Volume.

## License

MIT License - see LICENSE file for details.