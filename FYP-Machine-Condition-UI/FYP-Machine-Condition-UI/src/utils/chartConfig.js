// Chart.js configuration for time-series visualization
export const chartConfig = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
        mode: 'index',
        intersect: false,
    },
    plugins: {
        legend: {
            position: 'top',
            labels: {
                usePointStyle: true,
                padding: 15,
                color: '#e8eaed'
            }
        },
        title: {
            display: true,
            text: 'Lookback Window (240 points) + Forecast (60 points)',
            color: '#e8eaed',
            font: {
                size: 16,
                weight: 'bold'
            }
        },
        tooltip: {
            callbacks: {
                title: function(context) {
                    const date = new Date(context[0].parsed.x);
                    return date.toLocaleString();
                }
            }
        }
    },
    scales: {
        x: {
            type: 'time',
            time: {
                unit: 'minute',
                displayFormats: {
                    minute: 'HH:mm',
                    hour: 'MMM d, HH:mm'
                }
            },
            title: {
                display: true,
                text: 'Time',
                color: '#e8eaed'
            },
            ticks: {
                color: '#9aa0a6'
            },
            grid: {
                color: '#2d3748'
            }
        },
        y: {
            title: {
                display: true,
                text: 'Sensor Value',
                color: '#e8eaed'
            },
            ticks: {
                color: '#9aa0a6'
            },
            grid: {
                color: '#2d3748'
            },
            beginAtZero: false
        }
    }
};

// Feature names matching the backend (6 sensors)
export const FEATURE_NAMES = ['current', 'tempA', 'tempB', 'accX', 'accY', 'accZ'];

// Display names for the features
export const FEATURE_DISPLAY_NAMES = {
    current: 'Current (A)',
    tempA: 'Temperature A (°C)',
    tempB: 'Temperature B (°C)',
    accX: 'Acceleration X (g)',
    accY: 'Acceleration Y (g)',
    accZ: 'Acceleration Z (g)'
};

// Color palette for different sensors (lookback data - solid lines)
export const SENSOR_COLORS = {
    current: { line: 'rgba(255, 149, 0, 1)', fill: 'rgba(255, 149, 0, 0.15)' },
    tempA: { line: 'rgba(255, 59, 48, 1)', fill: 'rgba(255, 59, 48, 0.15)' },
    tempB: { line: 'rgba(0, 153, 255, 1)', fill: 'rgba(0, 153, 255, 0.15)' },
    accX: { line: 'rgba(255, 204, 0, 1)', fill: 'rgba(255, 204, 0, 0.15)' },
    accY: { line: 'rgba(0, 255, 136, 1)', fill: 'rgba(0, 255, 136, 0.15)' },
    accZ: { line: 'rgba(191, 90, 242, 1)', fill: 'rgba(191, 90, 242, 0.15)' }
};

// Forecast colors (dashed lines - distinct from lookback)
export const FORECAST_COLORS = {
    current: { line: 'rgba(255, 120, 0, 1)', fill: 'rgba(255, 120, 0, 0.2)' },
    tempA: { line: 'rgba(255, 80, 70, 1)', fill: 'rgba(255, 80, 70, 0.2)' },
    tempB: { line: 'rgba(0, 180, 255, 1)', fill: 'rgba(0, 180, 255, 0.2)' },
    accX: { line: 'rgba(255, 220, 50, 1)', fill: 'rgba(255, 220, 50, 0.2)' },
    accY: { line: 'rgba(50, 255, 160, 1)', fill: 'rgba(50, 255, 160, 0.2)' },
    accZ: { line: 'rgba(210, 120, 255, 1)', fill: 'rgba(210, 120, 255, 0.2)' }
};