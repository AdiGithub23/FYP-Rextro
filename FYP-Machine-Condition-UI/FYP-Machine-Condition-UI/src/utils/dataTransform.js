// src/utils/dataTransform.js

export const transformSensorData = (data) => {
    return data.map(point => ({
        timestamp: new Date(point.timestamp).getTime(),
        temp_body: point.temp_body,
        temp_shaft: point.temp_shaft,
        vibration_x: point.vibration_x,
        vibration_y: point.vibration_y,
        vibration_z: point.vibration_z,
        current: point.current,
    }));
};

export const transformForecastData = (forecast) => {
    return forecast.map((point, index) => ({
        timestamp: Date.now() + (index + 1) * 10000, // Assuming forecast is for every 10 seconds
        temp_body: point[0],
        temp_shaft: point[1],
        vibration_x: point[2],
        vibration_y: point[3],
        vibration_z: point[4],
        current: point[5],
    }));
};