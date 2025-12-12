import { useEffect, useState, useCallback } from 'react';
import { fetchForecastData, fetchLastLookback, fetchPreviousForecast } from '../services/api';

const useForecast = () => {
    const [lookbackData, setLookbackData] = useState([]);
    const [forecastData, setForecastData] = useState([]);
    const [previousForecastData, setPreviousForecastData] = useState([]);
    const [alerts, setAlerts] = useState({});
    const [metadata, setMetadata] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchData = useCallback(async () => {
        try {
            // Fetch lookback, forecast, and previous forecast data
            const [lookback, forecast, previousForecast] = await Promise.all([
                fetchLastLookback(),
                fetchForecastData(),
                fetchPreviousForecast()
            ]);
            
            console.log('useForecast - Lookback data:', lookback);
            console.log('useForecast - Forecast data:', forecast);
            console.log('useForecast - Previous forecast data:', previousForecast);
            
            setLookbackData(lookback);
            setForecastData(forecast.scaledForecast);
            setPreviousForecastData(previousForecast);
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

    return { 
        lookbackData, 
        forecastData, 
        previousForecastData, 
        alerts, 
        metadata, 
        loading, 
        error, 
        refetch: fetchData 
    };
};

export default useForecast;