// API utility functions for the trading dashboard

const API_BASE_URL = 'http://localhost:8000/api';

export interface FetchIndicatorParams {
  symbol: string;
  indicator: string;
  timeframe?: string;
  simulatedDate?: string | null;
  period?: number;
  fastPeriod?: number;
  slowPeriod?: number;
  signalPeriod?: number;
}

export const fetchIndicatorData = async (params: FetchIndicatorParams) => {
  const { symbol, indicator, timeframe = '5Y', simulatedDate, period, fastPeriod, slowPeriod, signalPeriod } = params;
  
  let endpoint = '';
  const urlParams = new URLSearchParams({
    timeframe,
    ...(simulatedDate && { simulated_date: simulatedDate })
  });

  switch (indicator) {
    case 'MACD':
      endpoint = `macd?fast_period=${fastPeriod || 12}&slow_period=${slowPeriod || 26}&signal_period=${signalPeriod || 9}`;
      break;
    case 'RSI':
      endpoint = `rsi?period=${period || 14}`;
      break;
    case 'VIX':
      endpoint = `vix?period=${period || 20}`;
      break;
    case 'OBV':
      endpoint = `obv`;
      break;
    case 'VPT':
      endpoint = `vpt`;
      break;
    default:
      throw new Error(`Unknown indicator: ${indicator}`);
  }

  const url = endpoint.includes('?') 
    ? `${API_BASE_URL}/indicators/${symbol}/${endpoint}&${urlParams}`
    : `${API_BASE_URL}/indicators/${symbol}/${endpoint}?${urlParams}`;
  
  console.log(`Fetching ${indicator} data from:`, url);
  const response = await fetch(url);
  console.log(`${indicator} response status:`, response.status);

  if (!response.ok) {
    throw new Error(`Failed to fetch ${indicator} data`);
  }

  const result = await response.json();
  console.log(`${indicator} response data:`, result);
  
  return result.data || [];
};

export const fetchStockData = async (symbol: string, timeframe: string, simulatedDate?: string | null) => {
  const params = new URLSearchParams({ timeframe });
  if (simulatedDate) params.append('simulated_date', simulatedDate);
  
  const response = await fetch(`${API_BASE_URL}/data/${symbol}?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch stock data for ${symbol}`);
  }
  
  const result = await response.json();
  return result.data || [];
};

export const fetchStocks = async () => {
  const response = await fetch(`${API_BASE_URL}/stocks/`);
  if (!response.ok) {
    throw new Error('Failed to fetch stocks');
  }
  return response.json();
};

export const fetchStockDetails = async (symbol: string, simulatedDate?: string | null) => {
  const params = new URLSearchParams();
  if (simulatedDate) params.append('simulated_date', simulatedDate);
  
  const response = await fetch(`${API_BASE_URL}/stocks/${symbol}/details?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch details for ${symbol}`);
  }
  return response.json();
};

export const fetchWatchlist = async (symbols: string[], simulatedDate?: string | null) => {
  const params = new URLSearchParams({
    symbols: symbols.join(',')
  });
  if (simulatedDate) params.append('simulated_date', simulatedDate);
  
  const response = await fetch(`${API_BASE_URL}/watchlist/?${params}`);
  if (!response.ok) {
    throw new Error('Failed to fetch watchlist');
  }
  return response.json();
};