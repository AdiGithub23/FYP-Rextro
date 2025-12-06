import { useEffect, useState, useCallback } from 'react';
import { fetchForecastData, fetchLastLookback } from '../services/api';

const useForecast = () => {
    const [lookbackData, setLookbackData] = useState([]);
    const [forecastData, setForecastData] = useState([]);
    const [alerts, setAlerts] = useState({});
    const [metadata, setMetadata] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchData = useCallback(async () => {
        try {
            // Fetch both lookback and forecast data
            const [lookback, forecast] = await Promise.all([
                fetchLastLookback(),
                fetchForecastData()
            ]);
            
            console.log('useForecast - Lookback data:', lookback);
            console.log('useForecast - Forecast data:', forecast);
            
            setLookbackData(lookback);
            setForecastData(forecast.scaledForecast);
            setAlerts(forecast.alerts);
            setMetadata(forecast.metadata);
            setLoading(false);
            setError(null);
        } catch (err) {
            console.error('useForecast - Error:', err);
            setError(err.message);
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
        // Fetch every 30 seconds to get updated data
        const intervalId = setInterval(fetchData, 30000);

        return () => clearInterval(intervalId);
    }, [fetchData]);

    return { lookbackData, forecastData, alerts, metadata, loading, error, refetch: fetchData };
};

export default useForecast;