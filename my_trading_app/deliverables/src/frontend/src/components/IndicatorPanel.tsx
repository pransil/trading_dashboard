import React, { useEffect, useState } from 'react';
import { CircularProgress, Typography, FormControl, Select, MenuItem } from '@mui/material';

interface IndicatorPanelProps {
  symbol: string;
  timeframe: string;
  simulatedDate: string | null;
  priceData: Array<{ date: string }>;
  priceDataLength: number;
  indicator: string;
  onIndicatorChange: (indicator: string) => void;
  availableIndicators: string[];
}

interface IndicatorPoint {
  date: string;
  value: number;
}

interface RSIPoint {
  date: string;
  rsi: number;
}

interface OBVPoint {
  date: string;
  obv: number;
}

interface VPTPoint {
  date: string;
  vpt: number;
}

interface VIXPoint {
  date: string;
  volatility: number;
}

interface MACDPoint {
  date: string;
  macd: number;
  signal: number;
  histogram: number;
}

const IndicatorPanel: React.FC<IndicatorPanelProps> = ({
  symbol,
  timeframe,
  simulatedDate,
  priceData,
  priceDataLength,
  indicator,
  onIndicatorChange,
  availableIndicators
}) => {
  const [indicatorData, setIndicatorData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mousePos, setMousePos] = useState<{x: number, y: number} | null>(null);

  // Define chart dimensions - match CandlestickChart padding
  const margin = { top: 10, right: 60, bottom: 30, left: 10 };
  const width = 800;
  const height = 200;
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  useEffect(() => {
    const fetchIndicatorData = async () => {
      if (!symbol) return;
      
      setLoading(true);
      setError(null);
      
      try {
        let endpoint = '';
        // Always fetch 5Y data for indicators to ensure enough historical data for calculations
        let params = new URLSearchParams({
          timeframe: '5Y',
          ...(simulatedDate && { simulated_date: simulatedDate })
        });

        switch (indicator) {
          case 'MACD':
            endpoint = `macd?fast_period=12&slow_period=26&signal_period=9`;
            break;
          case 'RSI':
            endpoint = `rsi?period=14`;
            break;
          case 'VIX':
            endpoint = `vix?period=20`;
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
          ? `http://localhost:8000/api/indicators/${symbol}/${endpoint}&${params}`
          : `http://localhost:8000/api/indicators/${symbol}/${endpoint}?${params}`;
        
        console.log(`Fetching ${indicator} data from:`, url);
        const response = await fetch(url);
        console.log(`${indicator} response status:`, response.status);

        if (!response.ok) {
          throw new Error(`Failed to fetch ${indicator} data`);
        }

        const result = await response.json();
        console.log(`${indicator} response data:`, result);
        
        // Filter the indicator data to match the price data date range
        let filteredData = result.data || [];
        if (priceData && priceData.length > 0 && filteredData.length > 0) {
          const firstPriceDate = priceData[0].date;
          const lastPriceDate = priceData[priceData.length - 1].date;
          
          filteredData = filteredData.filter((item: any) => 
            item.date >= firstPriceDate && item.date <= lastPriceDate
          );
          
          console.log(`Filtered ${indicator} data from ${result.data?.length || 0} to ${filteredData.length} points`);
        }
        
        setIndicatorData(filteredData);
      } catch (err) {
        console.error(`Error fetching ${indicator}:`, err);
        setError(err instanceof Error ? err.message : `Failed to fetch ${indicator}`);
      } finally {
        setLoading(false);
      }
    };

    fetchIndicatorData();
  }, [symbol, timeframe, simulatedDate, indicator, priceData]);

  const getDataForIndicator = () => {
    switch (indicator) {
      case 'RSI':
        return indicatorData.map((d: RSIPoint) => ({ date: d.date, value: d.rsi }));
      case 'VIX':
        return indicatorData.map((d: VIXPoint) => ({ date: d.date, value: d.volatility }));
      case 'OBV':
        return indicatorData.map((d: OBVPoint) => ({ date: d.date, value: d.obv }));
      case 'VPT':
        return indicatorData.map((d: VPTPoint) => ({ date: d.date, value: d.vpt }));
      case 'MACD':
        return indicatorData;
      default:
        return [];
    }
  };

  const renderIndicator = () => {
    if (loading) {
      return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
          <CircularProgress sx={{ color: 'white' }} />
        </div>
      );
    }

    if (error) {
      return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
          <Typography color="error">{error}</Typography>
        </div>
      );
    }

    const data = getDataForIndicator();
    if (!data || data.length === 0 || !priceData || priceDataLength === 0) {
      return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
          <Typography color="textSecondary">No data available</Typography>
        </div>
      );
    }

    // For MACD, use the existing MACDChart rendering logic
    if (indicator === 'MACD') {
      return renderMACDChart(data as MACDPoint[]);
    }

    // For other indicators, render a simple line chart
    return renderLineChart(data as IndicatorPoint[]);
  };

  const renderMACDChart = (macdData: MACDPoint[]) => {
    // Find min and max values for scaling
    const allValues = macdData.flatMap(d => [d.macd, d.signal, d.histogram].filter(v => !isNaN(v)));
    const minValue = Math.min(...allValues);
    const maxValue = Math.max(...allValues);
    const valueRange = maxValue - minValue;
    const padding = valueRange * 0.1;
    const yMin = minValue - padding;
    const yMax = maxValue + padding;

    // Create scales for plotting - map MACD data points to price chart coordinates
    const xScale = (index: number) => {
      if (!priceData || priceData.length === 0) {
        return (index / Math.max(macdData.length - 1, 1)) * chartWidth;
      }
      
      // Find the position of this MACD data point in the price data
      const macdDate = macdData[index]?.date;
      const priceIndex = priceData.findIndex(p => p.date === macdDate);
      
      if (priceIndex >= 0) {
        // Map to the same position as in the price chart
        return (priceIndex / Math.max(priceData.length - 1, 1)) * chartWidth;
      }
      
      // Fallback if date not found
      return (index / Math.max(macdData.length - 1, 1)) * chartWidth;
    };
    const yScale = (value: number) => {
      if (isNaN(value)) return chartHeight / 2;
      return chartHeight - ((value - yMin) / (yMax - yMin)) * chartHeight;
    };

    // Create lines
    const createLine = (data: MACDPoint[], getValue: (d: MACDPoint) => number) => {
      return data
        .map((d, i) => {
          const value = getValue(d);
          if (isNaN(value)) return '';
          return `${i === 0 ? 'M' : 'L'} ${xScale(i)} ${yScale(value)}`;
        })
        .join(' ');
    };

    return (
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="none"
        style={{ backgroundColor: '#000' }}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
        <g transform={`translate(${margin.left}, ${margin.top})`}>
          {/* Zero line */}
          <line
            x1={0}
            y1={yScale(0)}
            x2={chartWidth}
            y2={yScale(0)}
            stroke="#444"
            strokeDasharray="3,3"
          />

          {/* Histogram bars */}
          {macdData.map((d, i) => {
            if (isNaN(d.histogram)) return null;
            const barHeight = Math.abs(yScale(d.histogram) - yScale(0));
            const barY = d.histogram > 0 ? yScale(d.histogram) : yScale(0);
            const barWidth = Math.max(1, chartWidth / macdData.length - 1);
            
            return (
              <rect
                key={i}
                x={xScale(i) - barWidth / 2}
                y={barY}
                width={barWidth}
                height={barHeight}
                fill={d.histogram > 0 ? '#4caf50' : '#f44336'}
                opacity={0.7}
              />
            );
          })}

          {/* MACD line */}
          <path
            d={createLine(macdData, d => d.macd)}
            fill="none"
            stroke="#2196f3"
            strokeWidth="2"
          />

          {/* Signal line */}
          <path
            d={createLine(macdData, d => d.signal)}
            fill="none"
            stroke="#ff9800"
            strokeWidth="2"
          />

          {/* Y-axis labels - moved to right side */}
          <text x={chartWidth + 5} y={yScale(yMax)} fill="white" fontSize="10" textAnchor="start">
            {yMax.toFixed(2)}
          </text>
          <text x={chartWidth + 5} y={yScale(0)} fill="white" fontSize="10" textAnchor="start">
            0.00
          </text>
          <text x={chartWidth + 5} y={yScale(yMin)} fill="white" fontSize="10" textAnchor="start">
            {yMin.toFixed(2)}
          </text>

          {/* Legend */}
          <g transform={`translate(${chartWidth - 150}, 0)`}>
            <rect x={0} y={0} width={10} height={2} fill="#2196f3" />
            <text x={15} y={5} fill="white" fontSize="10">MACD</text>
            
            <rect x={0} y={10} width={10} height={2} fill="#ff9800" />
            <text x={15} y={15} fill="white" fontSize="10">Signal</text>
            
            <rect x={0} y={20} width={10} height={10} fill="#4caf50" opacity={0.7} />
            <text x={15} y={28} fill="white" fontSize="10">Histogram</text>
          </g>
        </g>

        {/* Crosshair for MACD */}
        {(() => {
          const crosshairData = getCrosshairData(macdData, yMin, yMax, chartHeight);
          if (!crosshairData) return null;

          return (
            <g>
              {/* Vertical line */}
              <line
                x1={crosshairData.x}
                y1={margin.top}
                x2={crosshairData.x}
                y2={height - margin.bottom}
                stroke="#666"
                strokeDasharray="3,3"
                strokeWidth="1"
              />
              {/* Horizontal line */}
              <line
                x1={margin.left}
                y1={crosshairData.y}
                x2={width - margin.right}
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
                  MACD: {crosshairData.value.toFixed(3)}
                </text>
              </g>
            </g>
          );
        })()}
      </svg>
    );
  };

  const renderLineChart = (data: IndicatorPoint[]) => {
    // Filter out invalid values
    const validData = data.filter(d => !isNaN(d.value) && d.value !== null);
    if (validData.length === 0) return null;

    // Find min and max values for scaling
    const values = validData.map(d => d.value);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const valueRange = maxValue - minValue || 1;
    const padding = valueRange * 0.1;
    const yMin = minValue - padding;
    const yMax = maxValue + padding;

    // Create scales for plotting - map indicator data points to price chart coordinates
    const xScale = (index: number) => {
      if (!priceData || priceData.length === 0) {
        return (index / Math.max(validData.length - 1, 1)) * chartWidth;
      }
      
      // Find the position of this indicator data point in the price data
      const indicatorDate = validData[index]?.date;
      const priceIndex = priceData.findIndex(p => p.date === indicatorDate);
      
      if (priceIndex >= 0) {
        // Map to the same position as in the price chart
        return (priceIndex / Math.max(priceData.length - 1, 1)) * chartWidth;
      }
      
      // Fallback if date not found
      return (index / Math.max(validData.length - 1, 1)) * chartWidth;
    };
    const yScale = (value: number) => {
      if (isNaN(value)) return chartHeight / 2;
      return chartHeight - ((value - yMin) / (yMax - yMin)) * chartHeight;
    };

    // Debug: Show latest values for verification
    if (validData.length > 0) {
      console.log(`${indicator} latest values:`, validData.slice(-3).map(d => ({ date: d.date, value: d.value.toFixed(2) })));
    }

    // Create line path
    const linePath = validData
      .map((d, i) => `${i === 0 ? 'M' : 'L'} ${xScale(i)} ${yScale(d.value)}`)
      .join(' ');

    // Determine color based on indicator
    const lineColor = {
      RSI: '#e91e63',
      VIX: '#3f51b5',
      OBV: '#00bcd4',
      VPT: '#9c27b0'
    }[indicator] || '#2196f3';

    // Add reference lines for RSI
    const referenceLines = [];
    if (indicator === 'RSI') {
      referenceLines.push(
        <line key="rsi-70" x1={0} y1={yScale(70)} x2={chartWidth} y2={yScale(70)} 
              stroke="#666" strokeDasharray="3,3" />,
        <line key="rsi-30" x1={0} y1={yScale(30)} x2={chartWidth} y2={yScale(30)} 
              stroke="#666" strokeDasharray="3,3" />
      );
    }

    return (
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="none"
        style={{ backgroundColor: '#000' }}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
        <g transform={`translate(${margin.left}, ${margin.top})`}>
          {/* Reference lines */}
          {referenceLines}

          {/* Main line */}
          <path
            d={linePath}
            fill="none"
            stroke={lineColor}
            strokeWidth="2"
          />

          {/* Y-axis labels - moved to right side */}
          <text x={chartWidth + 5} y={yScale(yMax)} fill="white" fontSize="10" textAnchor="start">
            {formatValue(yMax)}
          </text>
          <text x={chartWidth + 5} y={chartHeight / 2} fill="white" fontSize="10" textAnchor="start">
            {formatValue((yMax + yMin) / 2)}
          </text>
          <text x={chartWidth + 5} y={yScale(yMin)} fill="white" fontSize="10" textAnchor="start">
            {formatValue(yMin)}
          </text>

          {/* Indicator name */}
          <text x={chartWidth - 50} y={15} fill={lineColor} fontSize="12" fontWeight="bold">
            {indicator}
          </text>
        </g>

        {/* Crosshair for Line Chart */}
        {(() => {
          const crosshairData = getCrosshairData(validData, yMin, yMax, chartHeight);
          if (!crosshairData) return null;

          return (
            <g>
              {/* Vertical line */}
              <line
                x1={crosshairData.x}
                y1={margin.top}
                x2={crosshairData.x}
                y2={height - margin.bottom}
                stroke="#666"
                strokeDasharray="3,3"
                strokeWidth="1"
              />
              {/* Horizontal line */}
              <line
                x1={margin.left}
                y1={crosshairData.y}
                x2={width - margin.right}
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
                  {indicator}: {formatValue(crosshairData.value)}
                </text>
              </g>
            </g>
          );
        })()}
      </svg>
    );
  };

  const formatValue = (value: number): string => {
    if (indicator === 'OBV' || indicator === 'VPT') {
      // Format large numbers with abbreviations
      if (Math.abs(value) >= 1e9) return `${(value / 1e9).toFixed(1)}B`;
      if (Math.abs(value) >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
      if (Math.abs(value) >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
    }
    return value.toFixed(2);
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

  const getCrosshairData = (data: any[], yMin: number, yMax: number, chartHeight: number) => {
    if (!mousePos || data.length === 0 || !priceData || priceData.length === 0) return null;
    
    // Convert mouse position to data coordinates
    const chartX = mousePos.x - margin.left;
    const chartY = mousePos.y - margin.top;
    
    if (chartX < 0 || chartX > (width - margin.left - margin.right) || chartY < 0 || chartY > chartHeight) {
      return null;
    }
    
    // Calculate position in price data coordinates
    const chartWidth = width - margin.left - margin.right;
    const priceDataIndex = Math.round((chartX / chartWidth) * (priceDataLength - 1));
    const clampedPriceIndex = Math.max(0, Math.min(priceDataIndex, priceDataLength - 1));
    
    // Calculate value from y position
    const valueFromY = yMax - (chartY / chartHeight) * (yMax - yMin);
    
    // Get date from price data to ensure alignment
    const dateStr = priceData && priceData[clampedPriceIndex] ? priceData[clampedPriceIndex].date : '';
    
    return {
      date: dateStr,
      value: valueFromY,
      x: mousePos.x,
      y: mousePos.y
    };
  };

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      {/* Metrics Dropdown in upper left corner */}
      <div style={{ position: 'absolute', top: 5, left: 5, zIndex: 10 }}>
        <FormControl variant="outlined" size="small">
          <Select
            value={indicator}
            onChange={(e) => onIndicatorChange(e.target.value)}
            sx={{ 
              backgroundColor: 'rgba(0,0,0,0.7)',
              color: 'white', 
              '.MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.3)' },
              '.MuiSvgIcon-root': { color: 'white' },
              minWidth: 100,
              height: 30,
              fontSize: '0.875rem'
            }}
          >
            {availableIndicators.map((ind) => (
              <MenuItem key={ind} value={ind}>
                {ind}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </div>
      {renderIndicator()}
    </div>
  );
};

export default IndicatorPanel;