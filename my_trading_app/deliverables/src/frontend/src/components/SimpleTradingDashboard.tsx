import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Button,
  AppBar,
  Toolbar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  MenuItem,
  Select,
  FormControl,
  Alert,
  TextField,
} from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';
import CandlestickChart from './CandlestickChart';
import IndicatorPanel from './IndicatorPanel';

// Simple interfaces
interface Stock {
  symbol: string;
  name: string;
}

interface StockDetail {
  symbol: string;
  current_price: number;
  change: number;
  change_percent: number;
  volume: number;
  high_52w: number;
  low_52w: number;
}

interface WatchlistItem {
  symbol: string;
  last_price: number;
  net_change: number;
  change_percent: number;
  volume: number;
}

const SimpleTradingDashboard: React.FC = () => {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [selectedStock, setSelectedStock] = useState<string>('TSLA');
  const [stockDetail, setStockDetail] = useState<StockDetail | null>(null);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [timeframe, setTimeframe] = useState<string>('1Y');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [priceData, setPriceData] = useState<Array<{ date: string }>>([]);
  const [priceDataLength, setPriceDataLength] = useState<number>(0);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['EMA 12', 'EMA 26']);
  const [selectedIndicator, setSelectedIndicator] = useState<string>('MACD');
  const [simulatedDate, setSimulatedDate] = useState<string | null>(null);
  const [minDate, setMinDate] = useState<string>('');
  const [maxDate, setMaxDate] = useState<string>('');

  const API_BASE = 'http://localhost:8000/api';

  // Fetch available stocks
  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const response = await fetch(`${API_BASE}/stocks/`);
        if (!response.ok) throw new Error('Failed to fetch stocks');
        const data = await response.json();
        setStocks(data);
        setError('');
      } catch (err) {
        setError('Backend connection failed. Make sure the FastAPI server is running on port 8000.');
        console.error(err);
      }
    };
    fetchStocks();
  }, []);

  // Fetch stock details and date range when selection changes
  useEffect(() => {
    const fetchStockDetail = async () => {
      if (!selectedStock) return;
      
      try {
        setLoading(true);
        
        // Fetch stock details
        const detailsResponse = await fetch(`${API_BASE}/stocks/${selectedStock}/details`);
        if (!detailsResponse.ok) throw new Error('Failed to fetch stock details');
        const detailsData = await detailsResponse.json();
        setStockDetail(detailsData);
        
        // Fetch available date range for this stock
        const rangeResponse = await fetch(`${API_BASE}/data/${selectedStock}/range`);
        if (!rangeResponse.ok) {
          // If range endpoint doesn't exist, try to get it from data
          const dataResponse = await fetch(`${API_BASE}/data/${selectedStock}?timeframe=5Y`);
          if (dataResponse.ok) {
            const dataResult = await dataResponse.json();
            if (dataResult.data && dataResult.data.length > 0) {
              setMinDate(dataResult.data[0].date);
              setMaxDate(dataResult.data[dataResult.data.length - 1].date);
              // Set simulated date to the last available date by default
              if (!simulatedDate) {
                setSimulatedDate(dataResult.data[dataResult.data.length - 1].date);
              }
            }
          }
        } else {
          const rangeData = await rangeResponse.json();
          setMinDate(rangeData.min_date || '');
          setMaxDate(rangeData.max_date || '');
          // Set simulated date to the last available date by default
          if (!simulatedDate && rangeData.max_date) {
            setSimulatedDate(rangeData.max_date);
          }
        }
        
        setError('');
      } catch (err) {
        setError(`Failed to fetch details for ${selectedStock}`);
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchStockDetail();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedStock]);

  // Fetch watchlist
  useEffect(() => {
    const fetchWatchlist = async () => {
      try {
        const symbols = ['TSLA', 'AAPL', 'MSFT', 'GOOGL'];
        const response = await fetch(`${API_BASE}/watchlist/?symbols=${symbols.join(',')}`);
        if (!response.ok) throw new Error('Failed to fetch watchlist');
        const data = await response.json();
        setWatchlist(data);
      } catch (err) {
        console.error('Failed to fetch watchlist:', err);
      }
    };
    fetchWatchlist();
  }, []);

  const formatPrice = (price: number | string): string => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    if (isNaN(numPrice)) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(numPrice);
  };

  const formatPercent = (percent: number | string): string => {
    const numPercent = typeof percent === 'string' ? parseFloat(percent) : percent;
    if (isNaN(numPercent)) return '0.00%';
    const sign = numPercent >= 0 ? '+' : '';
    return `${sign}${numPercent.toFixed(2)}%`;
  };

  const formatVolume = (volume: number): string => {
    if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(1)}M`;
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(1)}K`;
    }
    return volume.toLocaleString();
  };

  const timeframes = ['1W', '1M', '3M', '6M', '1Y', 'YTD', '5Y'];
  const trendLines = ['EMA 12', 'EMA 26', 'SMA 12', 'SMA 26'];
  const indicators = ['MACD', 'RSI', 'VIX', 'OBV', 'VPT'];

  const handleMetricChange = (metric: string) => {
    setSelectedMetrics(prev => {
      if (prev.includes(metric)) {
        return prev.filter(m => m !== metric);
      } else {
        return [...prev, metric];
      }
    });
  };

  return (
    <div style={{ height: '100vh', backgroundColor: '#1a1a1a', overflow: 'hidden' }}>
      
      {/* Top App Bar */}
      <AppBar position="static" sx={{ backgroundColor: '#000000', borderBottom: '1px solid #333' }}>
        <Toolbar sx={{ minHeight: '48px', height: '48px' }}>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            📈 Trading Dashboard
          </Typography>
          
          {/* Stock Selector */}
          <FormControl variant="outlined" sx={{ mr: 2, minWidth: 120 }}>
            <Select
              value={selectedStock}
              onChange={(e) => setSelectedStock(e.target.value)}
              sx={{ 
                color: 'white', 
                '.MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.3)' },
                '.MuiSvgIcon-root': { color: 'white' }
              }}
              size="small"
            >
              {stocks.map((stock) => (
                <MenuItem key={stock.symbol} value={stock.symbol}>
                  {stock.symbol}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          
          
          {/* Timeframe Buttons */}
          <Box sx={{ display: 'flex', gap: 1 }}>
            {timeframes.map((tf) => (
              <Button
                key={tf}
                variant={timeframe === tf ? 'contained' : 'outlined'}
                onClick={() => setTimeframe(tf)}
                sx={{ 
                  color: 'white', 
                  borderColor: 'rgba(255,255,255,0.3)',
                  '&.MuiButton-contained': { 
                    backgroundColor: 'rgba(255,255,255,0.2)',
                    color: 'white'
                  }
                }}
                size="small"
              >
                {tf}
              </Button>
            ))}
          </Box>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <div style={{ padding: '4px', height: 'calc(100vh - 48px)' }}>
        
        {error && (
          <Alert severity="error" sx={{ mb: 1 }}>
            {error}
          </Alert>
        )}

        {/* Layout using CSS Flexbox instead of Material-UI Grid */}
        <div style={{ display: 'flex', gap: '4px', height: '100%' }}>
          
          {/* Left Column - Charts */}
          <div style={{ flex: '2', display: 'flex', flexDirection: 'column', gap: '4px', height: '100%' }}>
            
            {/* Main Price Chart - reduced height by 20% */}
            <Paper sx={{ p: 0.5, flex: '0.48', backgroundColor: '#0a0a0a', color: 'white', minHeight: 0 }}>
              <CandlestickChart 
                symbol={selectedStock} 
                timeframe={timeframe}
                simulatedDate={simulatedDate}
                onDataChange={(data, length) => {
                  setPriceData(data);
                  setPriceDataLength(length);
                }}
                selectedMetrics={selectedMetrics}
                onMetricsChange={setSelectedMetrics}
                availableTrendLines={trendLines}
              />
            </Paper>
            
            {/* Indicator Panel - increased height */}
            <Paper sx={{ p: 0.5, flex: '0.32', backgroundColor: '#0a0a0a', color: 'white', minHeight: 0 }}>
              <IndicatorPanel 
                symbol={selectedStock} 
                timeframe={timeframe}
                simulatedDate={simulatedDate}
                priceData={priceData}
                priceDataLength={priceDataLength}
                indicator={selectedIndicator}
                onIndicatorChange={setSelectedIndicator}
                availableIndicators={indicators}
              />
            </Paper>
            
          </div>
          
          {/* Right Column */}
          <div style={{ flex: '1', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            
            {/* Stock Details */}
            <Paper sx={{ p: 1.5, minHeight: '300px', backgroundColor: '#0a0a0a', color: 'white' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <Typography variant="h5" sx={{ color: '#4caf50', fontWeight: 'bold' }}>
                  {stockDetail?.symbol || selectedStock}
                </Typography>
                
                {/* Date Picker - Always visible */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.875rem' }}>
                    Display Date:
                  </Typography>
                  <TextField
                    type="date"
                    value={simulatedDate || ''}
                    onChange={(e) => setSimulatedDate(e.target.value)}
                    placeholder="YYYY-MM-DD"
                    inputProps={{
                      min: minDate,
                      max: maxDate,
                      style: { textAlign: 'center' },
                    }}
                  sx={{
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: 1,
                    minWidth: '140px',
                    '& .MuiInputBase-input': {
                      color: 'white',
                      padding: '8px 12px',
                      fontSize: '0.875rem',
                      fontFamily: 'monospace',
                      '&::placeholder': {
                        color: 'rgba(255, 255, 255, 0.5)',
                        opacity: 1,
                      },
                    },
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(255, 255, 255, 0.2)',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(255, 255, 255, 0.3)',
                    },
                    '& .Mui-focused .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#4caf50',
                    },
                    // Style for date input buttons (calendar icon, etc)
                    '& input[type="date"]::-webkit-calendar-picker-indicator': {
                      filter: 'invert(0.8)',
                      cursor: 'pointer',
                    },
                  }}
                  size="small"
                />
                </div>
              </div>
              
              {loading ? (
                <div style={{ display: 'flex', justifyContent: 'center', marginTop: '32px' }}>
                  <CircularProgress />
                </div>
              ) : stockDetail ? (
                <div>
                  <Typography variant="h3" sx={{ fontWeight: 'bold', mb: 2, color: 'white' }}>
                    {formatPrice(stockDetail.current_price)}
                  </Typography>
                  
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
                    {(typeof stockDetail.change === 'string' ? parseFloat(stockDetail.change) : stockDetail.change) >= 0 ? (
                      <TrendingUp sx={{ color: '#4caf50', mr: 1, fontSize: 28 }} />
                    ) : (
                      <TrendingDown sx={{ color: '#f44336', mr: 1, fontSize: 28 }} />
                    )}
                    <Typography
                      variant="h5"
                      sx={{ color: (typeof stockDetail.change === 'string' ? parseFloat(stockDetail.change) : stockDetail.change) >= 0 ? '#4caf50' : '#f44336', mr: 2 }}
                    >
                      {formatPrice(Math.abs(typeof stockDetail.change === 'string' ? parseFloat(stockDetail.change) : stockDetail.change))}
                    </Typography>
                    <Chip
                      label={formatPercent(stockDetail.change_percent)}
                      color={(typeof stockDetail.change === 'string' ? parseFloat(stockDetail.change) : stockDetail.change) >= 0 ? 'success' : 'error'}
                      sx={{ fontSize: '1rem', fontWeight: 'bold' }}
                    />
                  </div>

                  <hr style={{ margin: '16px 0', border: 'none', borderTop: '1px solid #eee' }} />

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                    <div>
                      <Typography variant="body2" sx={{ color: '#888' }} gutterBottom>
                        Volume
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'white' }}>
                        {formatVolume(stockDetail.volume)}
                      </Typography>
                    </div>
                    <div>
                      <Typography variant="body2" sx={{ color: '#888' }} gutterBottom>
                        52W High
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'white' }}>
                        {formatPrice(stockDetail.high_52w)}
                      </Typography>
                    </div>
                    <div>
                      <Typography variant="body2" sx={{ color: '#888' }} gutterBottom>
                        52W Low
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'white' }}>
                        {formatPrice(stockDetail.low_52w)}
                      </Typography>
                    </div>
                    <div>
                      <Typography variant="body2" sx={{ color: '#888' }} gutterBottom>
                        52W Range
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'white' }}>
                        {formatPrice(stockDetail.high_52w - stockDetail.low_52w)}
                      </Typography>
                    </div>
                  </div>
                </div>
              ) : (
                <Typography variant="h6" sx={{ color: '#888' }}>
                  No data available
                </Typography>
              )}
            </Paper>
            
            {/* Watchlist */}
            <Paper sx={{ p: 1, backgroundColor: '#0a0a0a', color: 'white' }}>
              <Typography variant="h6" gutterBottom sx={{ color: '#4caf50', fontWeight: 'bold' }}>
                📋 Watch List
              </Typography>
              
              {watchlist.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '24px' }}>
                  <CircularProgress size={24} />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Loading watchlist...
                  </Typography>
                </div>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Symbol</TableCell>
                        <TableCell align="right" sx={{ color: 'white', fontWeight: 'bold' }}>Price</TableCell>
                        <TableCell align="right" sx={{ color: 'white', fontWeight: 'bold' }}>Change</TableCell>
                        <TableCell align="right" sx={{ color: 'white', fontWeight: 'bold' }}>Volume</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {watchlist.map((item) => (
                        <TableRow
                          key={item.symbol}
                          hover
                          sx={{ 
                            cursor: 'pointer',
                            backgroundColor: selectedStock === item.symbol ? '#333' : 'inherit'
                          }}
                          onClick={() => setSelectedStock(item.symbol)}
                        >
                          <TableCell sx={{ color: 'white' }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'white' }}>
                              {item.symbol}
                            </Typography>
                          </TableCell>
                          <TableCell align="right" sx={{ color: 'white' }}>
                            <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'white' }}>
                              {formatPrice(item.last_price)}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                              {(typeof item.net_change === 'string' ? parseFloat(item.net_change) : item.net_change) >= 0 ? (
                                <TrendingUp sx={{ fontSize: 16, color: '#4caf50', marginRight: '4px' }} />
                              ) : (
                                <TrendingDown sx={{ fontSize: 16, color: '#f44336', marginRight: '4px' }} />
                              )}
                              <Typography
                                variant="body2"
                                sx={{ 
                                  color: (typeof item.net_change === 'string' ? parseFloat(item.net_change) : item.net_change) >= 0 ? '#4caf50' : '#f44336',
                                  fontWeight: 'bold'
                                }}
                              >
                                {formatPercent(item.change_percent)}
                              </Typography>
                            </div>
                          </TableCell>
                          <TableCell align="right" sx={{ color: 'white' }}>
                            <Typography variant="caption" sx={{ color: 'white' }}>
                              {formatVolume(item.volume)}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Paper>
            
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleTradingDashboard;