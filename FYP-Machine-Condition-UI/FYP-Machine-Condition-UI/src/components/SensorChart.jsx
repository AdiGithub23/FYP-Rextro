import React from 'react';
import { Line } from 'react-chartjs-2';
import useSensorData from '../hooks/useSensorData';
import useForecast from '../hooks/useForecast';
import { chartConfig } from '../utils/chartConfig';

const SensorChart = () => {
    const { sensorData, loading: loadingSensorData } = useSensorData();
    const { forecastData, loading: loadingForecastData } = useForecast();

    const loading = loadingSensorData || loadingForecastData;

    const data = {
        labels: sensorData.map(point => point.timestamp),
        datasets: [
            {
                label: 'Real-time Sensor Data',
                data: sensorData.map(point => point.temp_body), // Example for temp_body
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: true,
            },
            {
                label: 'Forecasted Data',
                data: forecastData.map(point => point.temp_body), // Example for temp_body
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                fill: true,
            },
        ],
    };

    return (
        <div>
            <h2>Sensor and Forecast Data</h2>
            {loading ? (
                <p>Loading...</p>
            ) : (
                <Line data={data} options={chartConfig} />
            )}
        </div>
    );
};

export default SensorChart;