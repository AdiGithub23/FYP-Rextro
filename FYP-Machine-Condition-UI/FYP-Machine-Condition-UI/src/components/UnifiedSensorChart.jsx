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

const UnifiedSensorChart = ({ selectedFeature = 'current' }) => {
    const { lookbackData, forecastData, loading, error } = useForecast();

    // Debug logs
    console.log('UnifiedSensorChart - Lookback Data:', lookbackData);
    console.log('UnifiedSensorChart - Forecast Data:', forecastData);

    // Prepare chart data
    const chartData = useMemo(() => {
        if (!lookbackData || !lookbackData.length) {
            return { labels: [], datasets: [] };
        }

        // Lookback data (last 240 points used for inference)
        const lookbackPoints = lookbackData.map(point => ({
            x: new Date(point.timestamp),
            y: point[selectedFeature]
        }));

        // Forecast data (60 predicted points)
        const forecastPoints = (forecastData || []).map(point => ({
            x: new Date(point.timestamp),
            y: point[selectedFeature]
        }));

        const datasets = [
            {
                label: `Lookback - ${FEATURE_DISPLAY_NAMES[selectedFeature] || selectedFeature}`,
                data: lookbackPoints,
                borderColor: SENSOR_COLORS[selectedFeature]?.line || 'rgba(75, 192, 192, 1)',
                backgroundColor: SENSOR_COLORS[selectedFeature]?.fill || 'rgba(75, 192, 192, 0.1)',
                borderWidth: 1.5,  // Thin solid line (matching notebook: linewidth=1.5)
                pointRadius: 0,
                pointHoverRadius: 4,
                fill: false,  // No fill for cleaner visualization
                tension: 0.1,
            }
        ];

        // Add forecast dataset if available
        if (forecastPoints.length > 0) {
            datasets.push({
                label: `Forecast - ${FEATURE_DISPLAY_NAMES[selectedFeature] || selectedFeature}`,
                data: forecastPoints,
                borderColor: FORECAST_COLORS[selectedFeature]?.line || 'rgba(255, 99, 132, 1)',
                backgroundColor: FORECAST_COLORS[selectedFeature]?.fill || 'rgba(255, 99, 132, 0.15)',
                borderWidth: 0.5,  // Thin dashed line (matching notebook: linewidth=2.5, scaled down for web)
                borderDash: [],  // Smaller dash pattern for cleaner look
                pointRadius: 0,
                pointHoverRadius: 5,
                fill: false,  // No fill for cleaner visualization
                tension: 0.1,
            });
        }

        return { datasets };
    }, [lookbackData, forecastData, selectedFeature]);

    // Custom options for this specific chart
    const chartOptions = useMemo(() => ({
        ...chartConfig,
        plugins: {
            ...chartConfig.plugins,
            title: {
                ...chartConfig.plugins.title,
                text: `${FEATURE_DISPLAY_NAMES[selectedFeature] || selectedFeature} - Lookback (240) + Forecast (60)`
            }
        }
    }), [selectedFeature]);

    if (loading) {
        return (
            <div className="chart-container" style={{ height: '350px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <p>Loading sensor data...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="chart-container" style={{ height: '350px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <p style={{ color: 'red' }}>Error: {error}</p>
            </div>
        );
    }

    if (!lookbackData || !lookbackData.length) {
        return (
            <div className="chart-container" style={{ height: '350px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f9f9f9', borderRadius: '8px' }}>
                <p>No lookback data available. Waiting for first inference cycle...</p>
            </div>
        );
    }

    return (
        <div className="chart-container" style={{ height: '350px', padding: '10px' }}>
            <Line data={chartData} options={chartOptions} />
        </div>
    );
};

export default UnifiedSensorChart;
