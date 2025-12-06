import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Feature names matching the backend (current, tempA, tempB, accX, accY, accZ)
export const FEATURE_NAMES = ['current', 'tempA', 'tempB', 'accX', 'accY', 'accZ'];

// Fetch the last lookback window (240 points used for inference)
export const fetchLastLookback = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/sensor/last-lookback`);
        return response.data.data || [];
    } catch (error) {
        console.error("Error fetching last lookback:", error);
        throw error;
    }
};

// Fetch buffer data (current rolling buffer)
export const fetchSensorBuffer = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/sensor/buffer`);
        return response.data.data || [];
    } catch (error) {
        console.error("Error fetching sensor buffer:", error);
        throw error;
    }
};

// Fetch latest prediction with both raw and scaled forecasts
export const fetchForecastData = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/inference/last-prediction`);
        const result = response.data;
        
        console.log('API Response:', result);
        
        if (result.status === 'success' && result.scaled_forecast) {
            // Use scaled_forecast_array for visualization (context-matched predictions)
            const scaledForecastArray = result.scaled_forecast_array || [];
            const rawForecastArray = result.raw_forecast_array || [];
            
            // Get the scaled forecast predictions with timestamps
            const scaledPredictions = result.scaled_forecast?.predictions || [];
            
            // Transform scaled forecast array into structured data
            const transformedScaledForecast = scaledPredictions.map((point, index) => ({
                timestamp: point.timestamp,
                step: point.step,
                current: point.current,
                tempA: point.tempA,
                tempB: point.tempB,
                accX: point.accX,
                accY: point.accY,
                accZ: point.accZ
            }));
            
            console.log('Transformed scaled forecast:', transformedScaledForecast);
            
            return {
                scaledForecast: transformedScaledForecast,
                rawForecast: rawForecastArray,
                alerts: result.alerts || {},
                metadata: {
                    forecast_horizon: result.scaled_forecast?.forecast_horizon || 60,
                    num_features: result.scaled_forecast?.num_features || 6,
                    inference_count: result.inference_count,
                    timestamp: result.timestamp
                }
            };
        }
        return { scaledForecast: [], rawForecast: [], alerts: {}, metadata: {} };
    } catch (error) {
        console.error("Error fetching forecast data:", error);
        throw error;
    }
};

// Fetch inference status
export const fetchInferenceStatus = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/inference/status`);
        return response.data.data || response.data;
    } catch (error) {
        console.error("Error fetching inference status:", error);
        throw error;
    }
};