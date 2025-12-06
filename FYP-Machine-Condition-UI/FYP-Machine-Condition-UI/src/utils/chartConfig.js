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
                padding: 15
            }
        },
        title: {
            display: true,
            text: 'Lookback Window (240 points) + Forecast (60 points)',
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
                text: 'Time'
            }
        },
        y: {
            title: {
                display: true,
                text: 'Sensor Value'
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
    current: { line: 'rgba(255, 159, 64, 1)', fill: 'rgba(255, 159, 64, 0.1)' },
    tempA: { line: 'rgba(255, 99, 132, 1)', fill: 'rgba(255, 99, 132, 0.1)' },
    tempB: { line: 'rgba(54, 162, 235, 1)', fill: 'rgba(54, 162, 235, 0.1)' },
    accX: { line: 'rgba(255, 206, 86, 1)', fill: 'rgba(255, 206, 86, 0.1)' },
    accY: { line: 'rgba(75, 192, 192, 1)', fill: 'rgba(75, 192, 192, 0.1)' },
    accZ: { line: 'rgba(153, 102, 255, 1)', fill: 'rgba(153, 102, 255, 0.1)' }
};

// Forecast colors (dashed lines - distinct from lookback)
export const FORECAST_COLORS = {
    current: { line: 'rgba(255, 100, 0, 1)', fill: 'rgba(255, 100, 0, 0.15)' },
    tempA: { line: 'rgba(220, 50, 80, 1)', fill: 'rgba(220, 50, 80, 0.15)' },
    tempB: { line: 'rgba(0, 120, 200, 1)', fill: 'rgba(0, 120, 200, 0.15)' },
    accX: { line: 'rgba(200, 160, 40, 1)', fill: 'rgba(200, 160, 40, 0.15)' },
    accY: { line: 'rgba(40, 160, 160, 1)', fill: 'rgba(40, 160, 160, 0.15)' },
    accZ: { line: 'rgba(120, 70, 220, 1)', fill: 'rgba(120, 70, 220, 0.15)' }
};