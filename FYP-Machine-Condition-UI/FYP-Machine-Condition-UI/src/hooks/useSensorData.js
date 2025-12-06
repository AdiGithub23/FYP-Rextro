import { useEffect, useState } from 'react';
import { fetchSensorBuffer } from '../services/api';

const useSensorData = () => {
    const [sensorData, setSensorData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const data = await fetchSensorBuffer();
                setSensorData(data);
                setError(null);
            } catch (err) {
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const intervalId = setInterval(fetchData, 10000); // Fetch every 10 seconds

        return () => clearInterval(intervalId); // Cleanup on unmount
    }, []);

    return { sensorData, loading, error };
};

export default useSensorData;