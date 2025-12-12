import React, { useMemo } from 'react';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale,
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import useForecast from '../hooks/useForecast';
import { chartConfig, SENSOR_COLORS, FORECAST_COLORS, FEATURE_DISPLAY_NAMES } from '../utils/chartConfig';

// Register Chart.js components
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale
);

const ComparisonChart = ({ selectedFeature = 'current' }) => {
    const { lookbackData, forecastData, previousForecastData, loading, error } = useForecast();

    // Calculate accuracy with tolerance band
    const accuracy = useMemo(() => {
        if (!lookbackData || !lookbackData.length || !previousForecastData || !previousForecastData.length) {
            return null;
        }

        const last60Lookback = lookbackData.slice(-60);
        const tolerancePercent = 20; // 20% tolerance band
        
        let pointsWithinTolerance = 0;
        const totalPoints = Math.min(last60Lookback.length, previousForecastData.length);

        for (let i = 0; i < totalPoints; i++) {
            const actualValue = last60Lookback[i][selectedFeature];
            const predictedValue = previousForecastData[i][selectedFeature];
            
            // Calculate tolerance band
            const tolerance = Math.abs(actualValue * (tolerancePercent / 100));
            const difference = Math.abs(actualValue - predictedValue);
            
            if (difference <= tolerance) {
                pointsWithinTolerance++;
            }
        }

        return ((pointsWithinTolerance / totalPoints) * 100).toFixed(1);
    }, [lookbackData, previousForecastData, selectedFeature]);

    // Prepare chart data - ONLY last 60 points comparison
    const chartData = useMemo(() => {
        if (!lookbackData || !lookbackData.length || !previousForecastData || !previousForecastData.length) {
            return { labels: [], datasets: [] };
        }

        // Get ONLY the last 60 lookback points (actual data)
        const last60Lookback = lookbackData.slice(-60);
        
        const last60ActualPoints = last60Lookback.map(point => ({
            x: new Date(point.timestamp),
            y: point[selectedFeature]
        }));

        // Map previous forecast values to the same timestamps
        const previousForecastPoints = previousForecastData.slice(0, 60).map((point, idx) => {
            const timestamp = idx < last60Lookback.length 
                ? new Date(last60Lookback[idx].timestamp)
                : new Date(last60Lookback[last60Lookback.length - 1].timestamp).getTime() + (idx - last60Lookback.length + 1) * 1000;
            
            return {
                x: timestamp,
                y: point[selectedFeature]
            };
        });

        const datasets = [
            {
                label: `Actual Data - ${FEATURE_DISPLAY_NAMES[selectedFeature] || selectedFeature}`,
                data: last60ActualPoints,
                borderColor: SENSOR_COLORS[selectedFeature]?.line || 'rgba(75, 192, 192, 1)',
                backgroundColor: SENSOR_COLORS[selectedFeature]?.fill || 'rgba(75, 192, 192, 0.1)',
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 4,
                fill: false,
                tension: 0.1,
            },
            {
                label: `Predicted Data - ${FEATURE_DISPLAY_NAMES[selectedFeature] || selectedFeature}`,
                data: previousForecastPoints,
                borderColor: FORECAST_COLORS[selectedFeature]?.line || 'rgba(255, 99, 132, 1)',
                backgroundColor: 'transparent',
                borderWidth: 2,
                borderDash: [8, 4],
                pointRadius: 0,
                pointHoverRadius: 4,
                fill: false,
                tension: 0.1,
            }
        ];

        return { datasets };
    }, [lookbackData, previousForecastData, selectedFeature]);

    // Custom options for comparison chart
    const chartOptions = useMemo(() => ({
        ...chartConfig,
        plugins: {
            ...chartConfig.plugins,
            title: {
                ...chartConfig.plugins.title,
                text: `${FEATURE_DISPLAY_NAMES[selectedFeature] || selectedFeature} - Last Inference Validation (60 points)`
            },
            subtitle: {
                display: true,
                text: 'Solid line: Actual data | Dashed line: What was predicted in previous inference',
                color: '#94a3b8',
                font: {
                    size: 11,
                    style: 'italic'
                }
            }
        }
    }), [selectedFeature]);

    if (loading) {
        return (
            <div className="chart-container" style={{ height: '350px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <p style={{ color: '#e2e8f0' }}>Loading comparison data...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="chart-container" style={{ height: '350px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <p style={{ color: '#ff3b30' }}>Error: {error}</p>
            </div>
        );
    }

    if (!lookbackData || !lookbackData.length || !previousForecastData || !previousForecastData.length) {
        return (
            <div className="chart-container" style={{ height: '350px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#1e293b', borderRadius: '8px' }}>
                <p style={{ color: '#e2e8f0' }}>
                    {!previousForecastData || !previousForecastData.length 
                        ? 'Waiting for at least 2 inference runs to compare predictions...'
                        : 'No data available. Waiting for first inference cycle...'}
                </p>
            </div>
        );
    }

    // Get color based on accuracy percentage
    const getAccuracyColor = (acc) => {
        if (acc >= 90) return '#22c55e'; // Green - Excellent
        if (acc >= 75) return '#3b82f6'; // Blue - Good
        if (acc >= 60) return '#f59e0b'; // Orange - Fair
        return '#ef4444'; // Red - Poor
    };

    return (
        <div style={{ position: 'relative' }}>
            {/* Accuracy Badge */}
            {accuracy !== null && (
                <div style={{
                    position: 'absolute',
                    top: '15px',
                    right: '15px',
                    background: getAccuracyColor(parseFloat(accuracy)),
                    color: '#ffffff',
                    padding: '8px 16px',
                    borderRadius: '20px',
                    fontWeight: 'bold',
                    fontSize: '14px',
                    zIndex: 10,
                    boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                }}>
                    <span>✓</span>
                    <span>{accuracy}% Accuracy</span>
                </div>
            )}
            
            <div className="chart-container" style={{ height: '350px', padding: '10px' }}>
                <Line data={chartData} options={chartOptions} />
            </div>
        </div>
    );
};

export default ComparisonChart;
