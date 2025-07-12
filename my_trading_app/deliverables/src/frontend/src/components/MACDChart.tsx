import React, { useState, useEffect } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

interface MACDData {
  date: string;
  macd: number;
  signal: number;
  histogram: number;
}

interface MACDChartProps {
  symbol: string;
  timeframe: string;
  simulatedDate: string | null;
  priceData?: Array<{ date: string }>;
  priceDataLength?: number;
}

const MACDChart: React.FC<MACDChartProps> = ({ symbol, timeframe, simulatedDate, priceData, priceDataLength }) => {
  const [data, setData] = useState<MACDData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams({ timeframe: '5Y' }); // Use 5Y for better MACD calculation
        if (simulatedDate) params.append('simulated_date', simulatedDate);
        
        const response = await fetch(`http://localhost:8000/api/indicators/${symbol}/macd?${params}`);
        if (response.ok) {
          const result = await response.json();
          let macdData = result.data || [];
          
          // Create aligned MACD data with same structure as price data
          if (priceData && priceData.length > 0) {
            const macdMap = new Map<string, MACDData>(macdData.map((item: MACDData) => [item.date, item]));
            const alignedData: MACDData[] = priceData.map((pricePoint): MACDData => {
              const macdPoint = macdMap.get(pricePoint.date);
              if (macdPoint) {
                return macdPoint;
              } else {
                return {
                  date: pricePoint.date,
                  macd: 0,
                  signal: 0,
                  histogram: 0
                };
              }
            });
            // Don't filter out zero values - keep exact same length as price data
            macdData = alignedData;
            console.log('Price data dates:', priceData.length, 'MACD data dates:', macdData.length);
          }
          
          setData(macdData);
        } else {
          setData([]);
        }
      } catch (error) {
        console.error('Error fetching MACD data:', error);
        setData([]);
      } finally {
        setLoading(false);
      }
    };

    if (symbol) {
      fetchData();
    }
  }, [symbol, timeframe, simulatedDate, priceData]);

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
        <Typography variant="body1" sx={{ color: '#666' }}>No MACD data available</Typography>
      </Box>
    );
  }

  // Calculate canvas dimensions
  const width = 800;
  const height = 200;
  const padding = { top: 20, right: 60, bottom: 40, left: 60 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Calculate value ranges with safe number conversion
  const macdValues = data.map(d => {
    const macd = typeof d.macd === 'string' ? parseFloat(d.macd) : d.macd;
    const signal = typeof d.signal === 'string' ? parseFloat(d.signal) : d.signal;
    const histogram = typeof d.histogram === 'string' ? parseFloat(d.histogram) : d.histogram;
    return [macd, signal, histogram].filter(v => !isNaN(v));
  }).flat();

  const minValue = Math.min(...macdValues) * 1.1;
  const maxValue = Math.max(...macdValues) * 1.1;
  const valueRange = maxValue - minValue;

  // Helper functions - map MACD points to exact price chart positions
  const xScale = (macdIndex: number) => {
    if (priceData && priceDataLength) {
      // Find the position of this MACD data point in the price data
      const macdDate = data[macdIndex]?.date;
      const priceIndex = priceData.findIndex(p => p.date === macdDate);
      if (priceIndex >= 0) {
        // Use the exact same position as the price chart
        return padding.left + (priceIndex * chartWidth) / (priceDataLength - 1);
      }
    }
    // Fallback to regular scaling if mapping fails
    return padding.left + (macdIndex * chartWidth) / (data.length - 1);
  };
  
  // Debug logging
  console.log('MACD Chart - data.length:', data.length, 'priceDataLength:', priceDataLength);
  const yScale = (value: number) => padding.top + ((maxValue - value) / valueRange) * chartHeight;

  return (
    <Box sx={{ position: 'relative', width: '100%', height: '100%' }}>
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="none"
        style={{ backgroundColor: '#000' }}
      >
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map(ratio => {
          const y = padding.top + ratio * chartHeight;
          const value = maxValue - ratio * valueRange;
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
                fontSize="10"
                textAnchor="start"
              >
                {value.toFixed(3)}
              </text>
            </g>
          );
        })}

        {/* Zero line */}
        {minValue <= 0 && maxValue >= 0 && (
          <line
            x1={padding.left}
            y1={yScale(0)}
            x2={width - padding.right}
            y2={yScale(0)}
            stroke="#666"
            strokeWidth="1"
          />
        )}

        {/* Histogram bars */}
        {data.map((point, index) => {
          const histogram = typeof point.histogram === 'string' ? parseFloat(point.histogram) : point.histogram;
          if (isNaN(histogram)) return null;

          const x = xScale(index);
          const barWidth = Math.max(1, chartWidth / data.length * 0.8);
          const zeroY = yScale(0);
          const histY = yScale(histogram);
          const barHeight = Math.abs(histY - zeroY);
          const barY = histogram >= 0 ? histY : zeroY;

          return (
            <rect
              key={`hist-${index}`}
              x={x - barWidth / 2}
              y={barY}
              width={barWidth}
              height={barHeight}
              fill={histogram >= 0 ? '#4caf5040' : '#f4433640'}
              stroke={histogram >= 0 ? '#4caf50' : '#f44336'}
              strokeWidth="0.5"
            />
          );
        })}

        {/* MACD Line */}
        {(() => {
          const macdPoints: string[] = [];
          data.forEach((point, index) => {
            const macd = typeof point.macd === 'string' ? parseFloat(point.macd) : point.macd;
            if (!isNaN(macd)) {
              const x = xScale(index);
              const y = yScale(macd);
              macdPoints.push(`${macdPoints.length === 0 ? 'M' : 'L'} ${x} ${y}`);
            }
          });

          const macdPath = macdPoints.join(' ');
          return macdPath && macdPoints.length > 0 ? (
            <path
              d={macdPath}
              fill="none"
              stroke="#2196f3"
              strokeWidth="2"
            />
          ) : null;
        })()}

        {/* Signal Line */}
        {(() => {
          const signalPoints: string[] = [];
          data.forEach((point, index) => {
            const signal = typeof point.signal === 'string' ? parseFloat(point.signal) : point.signal;
            if (!isNaN(signal)) {
              const x = xScale(index);
              const y = yScale(signal);
              signalPoints.push(`${signalPoints.length === 0 ? 'M' : 'L'} ${x} ${y}`);
            }
          });

          const signalPath = signalPoints.join(' ');
          return signalPath && signalPoints.length > 0 ? (
            <path
              d={signalPath}
              fill="none"
              stroke="#ff9800"
              strokeWidth="2"
            />
          ) : null;
        })()}

        {/* Date labels */}
        {data.filter((_, i) => i % Math.floor(data.length / 5) === 0).map((point, index) => {
          const actualIndex = data.indexOf(point);
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
              {new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            </text>
          );
        })}


        {/* Legend */}
        <g>
          <text
            x={width - padding.right - 180}
            y={15}
            fill="#2196f3"
            fontSize="10"
            fontWeight="bold"
          >
            ― MACD
          </text>
          <text
            x={width - padding.right - 130}
            y={15}
            fill="#ff9800"
            fontSize="10"
            fontWeight="bold"
          >
            ― Signal
          </text>
          <text
            x={width - padding.right - 80}
            y={15}
            fill="#666"
            fontSize="10"
            fontWeight="bold"
          >
            ▬ Histogram
          </text>
        </g>
      </svg>
    </Box>
  );
};

export default MACDChart;