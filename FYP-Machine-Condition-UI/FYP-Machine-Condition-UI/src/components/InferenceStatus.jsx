import React, { useState, useEffect } from 'react';
import { fetchInferenceStatus } from '../services/api';

const InferenceStatus = () => {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const getStatus = async () => {
            try {
                const data = await fetchInferenceStatus();
                setStatus(data);
                setError(null);
            } catch (err) {
                console.error('Error fetching inference status:', err);
                setError('Failed to fetch inference status');
            } finally {
                setLoading(false);
            }
        };

        getStatus();
        const intervalId = setInterval(getStatus, 10000); // Update every 10 seconds

        return () => clearInterval(intervalId);
    }, []);

    if (loading) {
        return (
            <div className="panel">
                <h3>Inference Status</h3>
                <p>Loading status...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="panel">
                <h3>Inference Status</h3>
                <p style={{ color: '#dc3545' }}>{error}</p>
            </div>
        );
    }

    const formatTime = (isoString) => {
        if (!isoString) return 'N/A';
        return new Date(isoString).toLocaleString();
    };

    return (
        <div className="panel">
            <h3 style={{ marginBottom: '15px' }}>Inference Status</h3>
            
            <div style={{ display: 'grid', gap: '12px' }}>
                {/* Status Badge */}
                <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '10px',
                    padding: '10px',
                    background: status?.status === 'running' ? '#d4edda' : '#f8d7da',
                    borderRadius: '8px'
                }}>
                    <span style={{ 
                        width: '12px', 
                        height: '12px', 
                        borderRadius: '50%', 
                        background: status?.status === 'running' ? '#28a745' : '#dc3545',
                        animation: status?.status === 'running' ? 'pulse 2s infinite' : 'none'
                    }} />
                    <strong>Status:</strong> 
                    <span style={{ textTransform: 'uppercase' }}>{status?.status || 'N/A'}</span>
                </div>

                {/* Stats Grid */}
                <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: '1fr 1fr', 
                    gap: '10px' 
                }}>
                    <div style={{ padding: '10px', background: '#f8f9fa', borderRadius: '6px' }}>
                        <div style={{ fontSize: '12px', color: '#666' }}>Inference Interval</div>
                        <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333' }}>
                            {status?.inference_interval_minutes?.toFixed(1) || 'N/A'} min
                        </div>
                    </div>
                    
                    <div style={{ padding: '10px', background: '#f8f9fa', borderRadius: '6px' }}>
                        <div style={{ fontSize: '12px', color: '#666' }}>Data Collection</div>
                        <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333' }}>
                            {status?.data_collection_interval_seconds || 'N/A'}s
                        </div>
                    </div>
                    
                    <div style={{ padding: '10px', background: '#e7f3ff', borderRadius: '6px' }}>
                        <div style={{ fontSize: '12px', color: '#666' }}>Context Window</div>
                        <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#0066cc' }}>
                            {status?.context_length || 240} pts
                        </div>
                    </div>
                    
                    <div style={{ padding: '10px', background: '#fff3e0', borderRadius: '6px' }}>
                        <div style={{ fontSize: '12px', color: '#666' }}>Forecast Horizon</div>
                        <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#e65100' }}>
                            {status?.prediction_length || 60} pts
                        </div>
                    </div>
                </div>

                {/* Buffer Status */}
                <div style={{ 
                    padding: '10px', 
                    background: status?.buffer_ready ? '#d4edda' : '#fff3cd',
                    borderRadius: '6px',
                    border: `1px solid ${status?.buffer_ready ? '#28a745' : '#ffc107'}`
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>
                            <strong>Buffer:</strong> {status?.buffer_size || 0} / {status?.context_length || 240}
                        </span>
                        <span style={{ 
                            padding: '2px 8px', 
                            borderRadius: '4px',
                            background: status?.buffer_ready ? '#28a745' : '#ffc107',
                            color: status?.buffer_ready ? 'white' : '#333',
                            fontSize: '11px',
                            fontWeight: 'bold'
                        }}>
                            {status?.buffer_ready ? 'READY' : 'FILLING'}
                        </span>
                    </div>
                    {/* Progress bar */}
                    <div style={{ 
                        marginTop: '8px', 
                        height: '6px', 
                        background: '#e9ecef', 
                        borderRadius: '3px',
                        overflow: 'hidden'
                    }}>
                        <div style={{
                            width: `${Math.min((status?.buffer_size / (status?.context_length || 240)) * 100, 100)}%`,
                            height: '100%',
                            background: status?.buffer_ready ? '#28a745' : '#ffc107',
                            transition: 'width 0.3s ease'
                        }} />
                    </div>
                </div>

                {/* Inference Count */}
                <div style={{ 
                    padding: '15px', 
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    borderRadius: '8px',
                    color: 'white',
                    textAlign: 'center'
                }}>
                    <div style={{ fontSize: '12px', opacity: 0.9 }}>Total Inferences Run</div>
                    <div style={{ fontSize: '36px', fontWeight: 'bold' }}>
                        {status?.total_inferences_run || 0}
                    </div>
                </div>

                {/* Timing Info */}
                <div style={{ fontSize: '12px', color: '#666' }}>
                    <p><strong>Last Inference:</strong> {formatTime(status?.last_inference_time)}</p>
                    <p><strong>Next Inference:</strong> {formatTime(status?.next_inference_time)}</p>
                </div>
            </div>

            <style>{`
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.5; }
                    100% { opacity: 1; }
                }
            `}</style>
        </div>
    );
};

export default InferenceStatus;