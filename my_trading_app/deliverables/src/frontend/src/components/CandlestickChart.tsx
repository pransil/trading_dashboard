import React, { useState, useEffect } from 'react';
import { Box, CircularProgress, Typography, FormControl, Select, MenuItem, Checkbox, ListItemText } from '@mui/material';

interface CandlestickData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface EMAPoint {
  date: string;
  ema: number;
}

interface CandlestickChartProps {
  symbol: string;
  timeframe: string;
  simulatedDate: string | null;
  onDataChange?: (data: Array<{ date: string }>, length: number) => void;
  selectedMetrics?: string[];
  onMetricsChange?: (metrics: string[]) => void;
  availableTrendLines?: string[];
}

const CandlestickChart: React.FC<CandlestickChartProps> = ({ 
  symbol, 
  timeframe, 
  simulatedDate, 
  onDataChange, 
  selectedMetrics = [], 
  onMetricsChange,
  availableTrendLines = []
}) => {
  const [data, setData] = useState<CandlestickData[]>([]);
  const [ema12Data, setEma12Data] = useState<EMAPoint[]>([]);
  const [ema26Data, setEma26Data] = useState<EMAPoint[]>([]);
  const [sma12Data, setSma12Data] = useState<EMAPoint[]>([]);
  const [sma26Data, setSma26Data] = useState<EMAPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [mousePos, setMousePos] = useState<{x: number, y: number} | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams({ timeframe });
        if (simulatedDate) params.append('simulated_date', simulatedDate);
        
        // Fetch price data
        const dataResponse = await fetch(`http://localhost:8000/api/data/${symbol}?${params}`);
        if (!dataResponse.ok) throw new Error('Failed to fetch data');
        const dataResult = await dataResponse.json();
        const priceData = dataResult.data || [];
        setData(priceData);
        
        // Notify parent component of the price data for MACD alignment
        if (onDataChange) {
          onDataChange(priceData.map((item: any) => ({ date: item.date })), priceData.length);
        }
        
        // Fetch indicator data with extended timeframe for better calculation
        const indicatorParams = new URLSearchParams({ timeframe: '5Y' }); // Always use 5Y for indicators to get full history
        if (simulatedDate) indicatorParams.append('simulated_date', simulatedDate);
        
        // Conditionally fetch indicators based on selectedMetrics
        if (selectedMetrics.includes('EMA 12')) {
          try {
            const ema12Response = await fetch(`http://localhost:8000/api/indicators/${symbol}/ema?period=12&${indicatorParams}`);
            if (ema12Response.ok) {
              const ema12Result = await ema12Response.json();
              setEma12Data(ema12Result.data || []);
            } else {
              setEma12Data([]);
            }
          } catch (error) {
            setEma12Data([]);
          }
        } else {
          setEma12Data([]);
        }
        
        if (selectedMetrics.includes('EMA 26')) {
          try {
            const ema26Response = await fetch(`http://localhost:8000/api/indicators/${symbol}/ema?period=26&${indicatorParams}`);
            if (ema26Response.ok) {
              const ema26Result = await ema26Response.json();
              setEma26Data(ema26Result.data || []);
            } else {
              setEma26Data([]);
            }
          } catch (error) {
            setEma26Data([]);
          }
        } else {
          setEma26Data([]);
        }
        
        if (selectedMetrics.includes('SMA 12')) {
          try {
            const sma12Response = await fetch(`http://localhost:8000/api/indicators/${symbol}/sma?period=12&${indicatorParams}`);
            if (sma12Response.ok) {
              const sma12Result = await sma12Response.json();
              setSma12Data(sma12Result.data || []);
            } else {
              setSma12Data([]);
            }
          } catch (error) {
            setSma12Data([]);
          }
        } else {
          setSma12Data([]);
        }
        
        if (selectedMetrics.includes('SMA 26')) {
          try {
            const sma26Response = await fetch(`http://localhost:8000/api/indicators/${symbol}/sma?period=26&${indicatorParams}`);
            if (sma26Response.ok) {
              const sma26Result = await sma26Response.json();
              setSma26Data(sma26Result.data || []);
            } else {
              setSma26Data([]);
            }
          } catch (error) {
            setSma26Data([]);
          }
        } else {
          setSma26Data([]);
        }
        
      } catch (error) {
        console.error('Error fetching chart data:', error);
        setData([]);
        setEma12Data([]);
        setEma26Data([]);
        setSma12Data([]);
        setSma26Data([]);
      } finally {
        setLoading(false);
      }
    };

    if (symbol) {
      fetchData();
    }
  }, [symbol, timeframe, simulatedDate, selectedMetrics]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress sx={{ color: '#4caf50' }} />
      </Box>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <Typography variant="body1" sx={{ color: '#666' }}>No data available</Typography>
      </Box>
    );
  }

  // Calculate canvas dimensions
  const width = 800;
  const height = 400;
  const padding = { top: 20, right: 60, bottom: 40, left: 10 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Calculate price range with safe number conversion
  const prices = data.flatMap(d => {
    const high = typeof d.high === 'string' ? parseFloat(d.high) : d.high;
    const low = typeof d.low === 'string' ? parseFloat(d.low) : d.low;
    return [high, low].filter(p => !isNaN(p));
  });
  const minPrice = Math.min(...prices) * 0.99;
  const maxPrice = Math.max(...prices) * 1.01;
  const priceRange = maxPrice - minPrice;

  // Calculate volume range with safe number conversion
  const volumes = data.map(d => {
    const volume = typeof d.volume === 'string' ? parseFloat(d.volume) : d.volume;
    return isNaN(volume) ? 0 : volume;
  });
  const maxVolume = Math.max(...volumes);

  // Helper functions
  const xScale = (index: number) => padding.left + (index * chartWidth) / (data.length - 1);
  const yScale = (price: number) => padding.top + ((maxPrice - price) / priceRange) * chartHeight;
  const volumeScale = (volume: number) => (volume / maxVolume) * (chartHeight * 0.2);

  const handleMetricChange = (metric: string) => {
    if (!onMetricsChange) return;
    
    const newMetrics = selectedMetrics.includes(metric)
      ? selectedMetrics.filter(m => m !== metric)
      : [...selectedMetrics, metric];
    
    onMetricsChange(newMetrics);
  };

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Convert to SVG coordinates
    const svgX = (x / rect.width) * width;
    const svgY = (y / rect.height) * height;
    
    setMousePos({ x: svgX, y: svgY });
  };

  const handleMouseLeave = () => {
    setMousePos(null);
  };

  const getCrosshairData = () => {
    if (!mousePos || data.length === 0) return null;
    
    // Convert mouse position to data coordinates
    const chartX = mousePos.x - padding.left;
    const chartY = mousePos.y - padding.top;
    
    if (chartX < 0 || chartX > chartWidth || chartY < 0 || chartY > chartHeight) {
      return null;
    }
    
    // Calculate data index from x position
    const dataIndex = Math.round((chartX / chartWidth) * (data.length - 1));
    const clampedIndex = Math.max(0, Math.min(dataIndex, data.length - 1));
    
    // Calculate price from y position
    const priceFromY = maxPrice - (chartY / chartHeight) * priceRange;
    
    // Get date from data
    const dateStr = data[clampedIndex]?.date || '';
    
    return {
      date: dateStr,
      price: priceFromY,
      x: mousePos.x,
      y: mousePos.y
    };
  };

  return (
    <Box sx={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Trend Lines Dropdown in upper left corner */}
      {onMetricsChange && availableTrendLines.length > 0 && (
        <Box sx={{ position: 'absolute', top: 5, left: 5, zIndex: 10 }}>
          <FormControl variant="outlined" size="small">
            <Select
              multiple
              value={selectedMetrics}
              onChange={(e) => onMetricsChange(e.target.value as string[])}
              renderValue={(selected) => `Trend Lines (${selected.length})`}
              sx={{ 
                backgroundColor: 'rgba(0,0,0,0.7)',
                color: 'white', 
                '.MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.3)' },
                '.MuiSvgIcon-root': { color: 'white' },
                minWidth: 140,
                height: 30,
                fontSize: '0.875rem'
              }}
              MenuProps={{
                PaperProps: {
                  sx: {
                    backgroundColor: '#000',
                    '& .MuiMenuItem-root': {
                      color: 'white',
                      '&:hover': {
                        backgroundColor: '#333'
                      },
                      '&.Mui-selected': {
                        backgroundColor: '#444'
                      }
                    }
                  }
                }
              }}
            >
              {availableTrendLines.map((metric) => (
                <MenuItem key={metric} value={metric}>
                  <Checkbox 
                    checked={selectedMetrics.includes(metric)} 
                    onChange={() => handleMetricChange(metric)}
                    sx={{ 
                      color: 'white',
                      '&.Mui-checked': { color: '#4caf50' }
                    }}
                  />
                  <ListItemText primary={metric} sx={{ color: 'white' }} />
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      )}
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="none"
        style={{ backgroundColor: '#000' }}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map(ratio => {
          const y = padding.top + ratio * chartHeight;
          const price = maxPrice - ratio * priceRange;
          return (
            <g key={ratio}>
              <line
                x1={padding.left}
                y1={y}
                x2={width - padding.right}
                y2={y}
                stroke="#333"
                strokeDasharray="3,3"
              />
              <text
                x={width - padding.right + 5}
                y={y + 4}
                fill="#666"
                fontSize="12"
                textAnchor="start"
              >
                ${price.toFixed(2)}
              </text>
            </g>
          );
        })}

        {/* Volume bars */}
        {data.map((candle, index) => {
          const x = xScale(index);
          const barWidth = chartWidth / data.length * 0.6;
          
          // Safe conversion for volume and prices
          const volume = typeof candle.volume === 'string' ? parseFloat(candle.volume) : candle.volume;
          const close = typeof candle.close === 'string' ? parseFloat(candle.close) : candle.close;
          const open = typeof candle.open === 'string' ? parseFloat(candle.open) : candle.open;
          
          if (isNaN(volume) || isNaN(close) || isNaN(open)) {
            return null;
          }
          
          const volumeHeight = volumeScale(volume);
          const volumeY = height - padding.bottom - volumeHeight;
          
          return (
            <rect
              key={`volume-${index}`}
              x={x - barWidth / 2}
              y={volumeY}
              width={barWidth}
              height={volumeHeight}
              fill={close >= open ? '#4caf5033' : '#f4433633'}
            />
          );
        })}

        {/* Candlesticks */}
        {data.map((candle, index) => {
          const x = xScale(index);
          
          // Safe number conversion
          const open = typeof candle.open === 'string' ? parseFloat(candle.open) : candle.open;
          const close = typeof candle.close === 'string' ? parseFloat(candle.close) : candle.close;
          const high = typeof candle.high === 'string' ? parseFloat(candle.high) : candle.high;
          const low = typeof candle.low === 'string' ? parseFloat(candle.low) : candle.low;
          
          // Skip if any value is invalid
          if (isNaN(open) || isNaN(close) || isNaN(high) || isNaN(low)) {
            return null;
          }
          
          const openY = yScale(open);
          const closeY = yScale(close);
          const highY = yScale(high);
          const lowY = yScale(low);
          
          const isGreen = close >= open;
          const color = isGreen ? '#4caf50' : '#f44336';
          const bodyTop = Math.min(openY, closeY);
          const bodyHeight = Math.abs(closeY - openY) || 1;
          const candleWidth = chartWidth / data.length * 0.6;

          return (
            <g key={`candle-${index}`}>
              {/* Wick */}
              <line
                x1={x}
                y1={highY}
                x2={x}
                y2={lowY}
                stroke={color}
                strokeWidth="1"
              />
              
              {/* Body */}
              <rect
                x={x - candleWidth / 2}
                y={bodyTop}
                width={candleWidth}
                height={bodyHeight}
                fill={color}
                stroke={color}
                strokeWidth="1"
              />
            </g>
          );
        })}

        {/* Technical Indicator Lines */}
        {(() => {
          const renderIndicatorLine = (indicatorData: EMAPoint[], color: string, label: string) => {
            if (indicatorData.length === 0 || data.length === 0) return null;
            
            const points: string[] = [];
            data.forEach((candle, index) => {
              const matchingIndicator = indicatorData.find(ind => ind.date === candle.date);
              if (matchingIndicator) {
                const value = typeof matchingIndicator.ema === 'string' ? parseFloat(matchingIndicator.ema) : matchingIndicator.ema;
                if (!isNaN(value)) {
                  const x = xScale(index);
                  const y = yScale(value);
                  points.push(`${points.length === 0 ? 'M' : 'L'} ${x} ${y}`);
                }
              }
            });

            const path = points.join(' ');
            return path && points.length > 0 ? (
              <path
                key={label}
                d={path}
                fill="none"
                stroke={color}
                strokeWidth="2"
                opacity="0.9"
              />
            ) : null;
          };

          return (
            <g>
              {selectedMetrics.includes('EMA 12') && renderIndicatorLine(ema12Data, '#ff9800', 'EMA 12')}
              {selectedMetrics.includes('EMA 26') && renderIndicatorLine(ema26Data, '#2196f3', 'EMA 26')}
              {selectedMetrics.includes('SMA 12') && renderIndicatorLine(sma12Data, '#4caf50', 'SMA 12')}
              {selectedMetrics.includes('SMA 26') && renderIndicatorLine(sma26Data, '#9c27b0', 'SMA 26')}
            </g>
          );
        })()}

        {/* Latest price label */}
        {data.length > 0 && (() => {
          const lastCandle = data[data.length - 1];
          const closePrice = typeof lastCandle.close === 'string' ? parseFloat(lastCandle.close) : lastCandle.close;
          const openPrice = typeof lastCandle.open === 'string' ? parseFloat(lastCandle.open) : lastCandle.open;
          
          return (
            <g>
              <rect
                x={width - padding.right + 5}
                y={yScale(closePrice) - 10}
                width={55}
                height={20}
                fill={closePrice >= openPrice ? '#4caf50' : '#f44336'}
                rx="2"
              />
              <text
                x={width - padding.right + 32}
                y={yScale(closePrice) + 4}
                fill="white"
                fontSize="12"
                textAnchor="middle"
                fontWeight="bold"
              >
                ${isNaN(closePrice) ? '0.00' : closePrice.toFixed(2)}
              </text>
            </g>
          );
        })()}

        {/* Date labels */}
        {data.filter((_, i) => i % Math.floor(data.length / 5) === 0).map((candle, index, arr) => {
          const actualIndex = data.indexOf(candle);
          const x = xScale(actualIndex);
          return (
            <text
              key={`date-${actualIndex}`}
              x={x}
              y={height - padding.bottom + 15}
              fill="#666"
              fontSize="10"
              textAnchor="middle"
            >
              {(() => {
                const [year, month, day] = candle.date.split('-').map(Number);
                const date = new Date(year, month - 1, day);
                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
              })()}
            </text>
          );
        })}


        {/* Indicators Legend */}
        {selectedMetrics.length > 0 && (() => {
          const legendItems = [
            { metric: 'EMA 12', color: '#ff9800', data: ema12Data },
            { metric: 'EMA 26', color: '#2196f3', data: ema26Data },
            { metric: 'SMA 12', color: '#4caf50', data: sma12Data },
            { metric: 'SMA 26', color: '#9c27b0', data: sma26Data },
          ].filter(item => selectedMetrics.includes(item.metric) && item.data.length > 0);

          return (
            <g>
              {legendItems.map((item, index) => (
                <text
                  key={item.metric}
                  x={width - padding.right - (legendItems.length - index) * 80}
                  y={15}
                  fill={item.color}
                  fontSize="10"
                  fontWeight="bold"
                >
                  ― {item.metric}
                </text>
              ))}
            </g>
          );
        })()}

        {/* Volume label */}
        <text
          x={padding.left}
          y={height - padding.bottom + 35}
          fill="#666"
          fontSize="10"
        >
          Volume
        </text>

        {/* Crosshair */}
        {(() => {
          const crosshairData = getCrosshairData();
          if (!crosshairData) return null;

          return (
            <g>
              {/* Vertical line */}
              <line
                x1={crosshairData.x}
                y1={padding.top}
                x2={crosshairData.x}
                y2={height - padding.bottom}
                stroke="#666"
                strokeDasharray="3,3"
                strokeWidth="1"
              />
              {/* Horizontal line */}
              <line
                x1={padding.left}
                y1={crosshairData.y}
                x2={width - padding.right}
                y2={crosshairData.y}
                stroke="#666"
                strokeDasharray="3,3"
                strokeWidth="1"
              />
              {/* Value display */}
              <g transform={`translate(${crosshairData.x + 10}, ${crosshairData.y - 10})`}>
                <rect
                  x={0}
                  y={0}
                  width={120}
                  height={30}
                  fill="rgba(0,0,0,0.8)"
                  stroke="#666"
                  rx={3}
                />
                <text x={5} y={12} fill="white" fontSize="10">
                  {(() => {
                    const [year, month, day] = crosshairData.date.split('-').map(Number);
                    const date = new Date(year, month - 1, day);
                    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                  })()}
                </text>
                <text x={5} y={24} fill="white" fontSize="10">
                  ${crosshairData.price.toFixed(2)}
                </text>
              </g>
            </g>
          );
        })()}
      </svg>
    </Box>
  );
};

export default CandlestickChart;