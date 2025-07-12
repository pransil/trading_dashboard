# my_trading_app - Trading Dashboard PRD

## Introduction
- **Problem Statement**: Traders need a comprehensive dashboard to visualize historical stock data with technical indicators, but existing solutions don't provide an integrated view with customizable time-based simulation capabilities for backtesting and analysis.
- **Solution Summary**: A web-based trading dashboard that loads historical stock data from CSV files, allows users to simulate any historical date as "current", and displays multiple synchronized panels showing candlestick charts, technical indicators (EMA, MACD), stock details, and a customizable watchlist.
- **Primary Goal**: Enable traders to analyze historical stock performance through time-based simulation, with synchronized technical indicators and multi-stock monitoring capabilities.

## User Stories
- As a trader, I want to select any historical date as "simulated current date" so that I can analyze stock performance as if I were trading on that day
- As a trader, I want to view candlestick charts with OHLC data and volume so that I can analyze price movements and trading patterns
- As a trader, I want to see synchronized MACD indicators below the price chart so that I can identify momentum and trend changes
- As a trader, I want to view exponential moving averages on the price chart so that I can identify trend directions
- As a trader, I want to switch between different time ranges (1W, 1M, 1Y, YTD, etc.) so that I can analyze different timeframes
- As a trader, I want to see detailed stock information (price, change %, 52W range, volume) so that I can make informed decisions
- As a trader, I want to maintain a watchlist of multiple stocks so that I can monitor several opportunities simultaneously
- As a trader, I want all panels to respect the simulated date so that I can backtest strategies without future data leakage

## Functional Requirements

### Data & Market Feeds
1. The system must load historical stock data from CSV files located in `/Users/patransil/dev/prediction/kaggle_stock_data`
2. The system must import CSV data (Date, Open, High, Low, Close, Adj Close, Volume) into a PostgreSQL "History DB"
3. The system must support a "Simulated Date" selector that treats the selected date as "current" for all displays
4. The system must prevent display of any data after the simulated date (no future data leakage)
5. The system must calculate and display Exponential Moving Average (EMA) on the main chart
6. The system must calculate and display MACD (Moving Average Convergence Divergence) in a synchronized panel
7. The system must support multiple timeframe views: 1 week, 1 month, 3 months, 6 months, 1 year, YTD, 5 years

### Display Panels & UI Components
8. The system must display a candlestick chart (History Chart) showing OHLC data with volume bars
9. The system must display stock details panel showing: current price, $ change, % change, 52-week range, volume
10. The system must display a MACD indicator panel directly below and synchronized with the main chart
11. The system must provide a watchlist panel showing multiple stocks with real-time (simulated date) metrics
12. The watchlist must show: Symbol, Net Change ($), Change (%), Last Price, Volume for each stock
13. All panels must update when the simulated date or selected stock changes

### User Interaction & Navigation
14. The system must allow users to search and select any stock from the loaded database
15. The system must allow users to add/remove stocks from their watchlist
16. The system must allow users to change the simulated date using a date picker
17. The system must allow users to zoom and pan within the chart timeframe
18. The system must synchronize all chart interactions (zoom, pan) between the price and MACD panels
19. The system must remember user preferences (watchlist, selected stock, timeframe)

## Non-Goals (Out of Scope)
- Real-time market data feeds (using historical data only)
- Actual trading or order execution
- Portfolio management or position tracking
- Options, futures, or other derivatives
- Social features or multi-user support
- Mobile application (web-only)
- Financial advice or recommendations

## Technical Considerations
- **Frontend**: React with Material-UI for UI components, Chart.js or D3.js for candlestick charts
- **Backend**: Python FastAPI for REST API endpoints
- **Database**: PostgreSQL for storing imported historical data ("History DB")
- **Data Source**: CSV files from `/Users/patransil/dev/prediction/kaggle_stock_data`
- **Data Import**: Batch process to load all CSV files into PostgreSQL on startup
- **Chart Library**: Lightweight financial charting library for candlestick, volume, and MACD displays
- **State Management**: Redux Toolkit for managing selected stock, date, and watchlist
- **Performance**: Charts should render within 500ms of data selection
- **Caching**: Redis for caching calculated indicators (EMA, MACD) to improve performance

## Success Metrics
- **Data Import**: Successfully load 100% of CSV files into PostgreSQL within 2 minutes
- **Chart Performance**: Render candlestick charts within 500ms of stock/date selection
- **Calculation Accuracy**: 100% accuracy for EMA and MACD calculations compared to standard formulas
- **UI Responsiveness**: All user interactions respond within 200ms
- **Simulated Date Integrity**: Zero instances of future data leakage in any view
- **Concurrent Charts**: Support at least 20 stocks in watchlist without performance degradation
- **Data Coverage**: Display data for any valid historical date in the dataset