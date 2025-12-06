import React from 'react';
import { Line } from 'react-chartjs-2';
import { useForecast } from '../hooks/useForecast';
import { useSensorData } from '../hooks/useSensorData';
import { chartConfig } from '../utils/chartConfig';

const ForecastChart = () => {
    const { sensorData } = useSensorData();
    const { forecastData } = useForecast();

    const chartData = {
        labels: sensorData.map(point => point.timestamp),
        datasets: [
            {
                label: 'Real-time Sensor Data',
                data: sensorData.map(point => point.value), // Adjust according to your data structure
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: true,
            },
            {
                label: 'Forecasted Data',
                data: forecastData.map(point => point.value), // Adjust according to your data structure
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                fill: true,
            },
        ],
    };

    return (
        <div>
            <h2>Forecast and Real-time Data</h2>
            <Line data={chartData} options={chartConfig} />
        </div>
    );
};

export default ForecastChart;