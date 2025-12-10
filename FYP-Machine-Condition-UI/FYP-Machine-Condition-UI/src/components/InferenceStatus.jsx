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
                <h3 style={{ fontSize: '18px', color: '#ffffff' }}>Inference Status</h3>
                <p style={{ color: '#e2e8f0', fontSize: '14px' }}>Loading status...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="panel">
                <h3 style={{ fontSize: '18px', color: '#ffffff' }}>Inference Status</h3>
                <p style={{ color: '#ff3b30', fontSize: '14px', fontWeight: '500' }}>{error}</p>
            </div>
        );
    }

    const formatTime = (isoString) => {
        if (!isoString) return 'N/A';
        return new Date(isoString).toLocaleString();
    };

    return (
        <div className="panel" style={{ background: '#1e293b' }}>
            <h3 style={{ marginBottom: '15px', fontSize: '18px', color: '#ffffff', fontWeight: 'bold' }}>Inference Status</h3>
            
            <div style={{ display: 'grid', gap: '12px', background: '#1e293b', padding: '0' }}>
                {/* Status Badge */}
                <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '10px',
                    padding: '12px 15px',
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px'
                }}>
                    <span style={{ 
                        width: '10px', 
                        height: '10px', 
                        borderRadius: '50%', 
                        background: '#22c55e',
                        animation: status?.status === 'running' ? 'pulse 2s infinite' : 'none'
                    }} />
                    <span style={{ textTransform: 'uppercase', fontSize: '16px', fontWeight: 'bold', color: '#f8fafc', flex: 1 }}>{status?.status || 'N/A'}</span>
                </div>

                {/* Stats Grid */}
                <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: '1fr 1fr', 
                    gap: '10px' 
                }}>
                    <div style={{ padding: '12px', background: '#0f172a', border: '1px solid #1e293b', borderRadius: '6px' }}>
                        <div style={{ fontSize: '12px', color: '#94a3b8', fontWeight: '500', marginBottom: '4px' }}>Inference Interval</div>
                        <div style={{ fontSize: '22px', fontWeight: 'bold', color: '#f8fafc' }}>
                            {status?.inference_interval_minutes?.toFixed(1) || 'N/A'} min
                        </div>
                    </div>
                    
                    <div style={{ padding: '12px', background: '#0f172a', border: '1px solid #1e293b', borderRadius: '6px' }}>
                        <div style={{ fontSize: '12px', color: '#94a3b8', fontWeight: '500', marginBottom: '4px' }}>Data Collection</div>
                        <div style={{ fontSize: '22px', fontWeight: 'bold', color: '#f8fafc' }}>
                            {status?.data_collection_interval_seconds || 'N/A'}s
                        </div>
                    </div>
                    
                    <div style={{ padding: '12px', background: '#0f172a', border: '1px solid #1e293b', borderRadius: '6px' }}>
                        <div style={{ fontSize: '12px', color: '#94a3b8', fontWeight: '500', marginBottom: '4px' }}>Context Window</div>
                        <div style={{ fontSize: '22px', fontWeight: 'bold', color: '#f8fafc' }}>
                            {status?.context_length || 240} pts
                        </div>
                    </div>
                    
                    <div style={{ padding: '12px', background: '#0f172a', border: '1px solid #1e293b', borderRadius: '6px' }}>
                        <div style={{ fontSize: '12px', color: '#94a3b8', fontWeight: '500', marginBottom: '4px' }}>Forecast Horizon</div>
                        <div style={{ fontSize: '22px', fontWeight: 'bold', color: '#f8fafc' }}>
                            {status?.prediction_length || 60} pts
                        </div>
                    </div>
                </div>

                {/* Buffer Status */}
                <div style={{ 
                    padding: '12px 15px', 
                    background: '#1e293b',
                    borderRadius: '6px',
                    border: '1px solid #334155'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '14px', color: '#f8fafc', fontWeight: '600' }}>
                            Buffer: {status?.buffer_size || 0} / {status?.context_length || 240}
                        </span>
                        <span style={{ 
                            padding: '3px 10px', 
                            borderRadius: '4px',
                            // background: '#22c55e',
                            background: '#3b82f6',
                            color: '#0f172a',
                            fontSize: '11px',
                            fontWeight: 'bold'
                        }}>
                            {status?.buffer_ready ? 'READY' : 'FILLING'}
                        </span>
                    </div>
                    {/* Progress bar */}
                    <div style={{ 
                        marginTop: '10px', 
                        height: '8px', 
                        background: '#0f172a', 
                        border: 'none',
                        borderRadius: '4px',
                        overflow: 'hidden'
                    }}>
                        <div style={{
                            width: `${Math.min((status?.buffer_size / (status?.context_length || 240)) * 100, 100)}%`,
                            height: '100%',
                            // background: '#22c55e',
                            background: '#3b82f6',
                            transition: 'width 0.3s ease'
                        }} />
                    </div>
                </div>

                {/* Inference Count */}
                <div style={{ 
                    padding: '20px', 
                    background: '#1e293b',
                    borderRadius: '8px',
                    color: 'white',
                    textAlign: 'center',
                    border: '1px solid #334155'
                }}>
                    <div style={{ fontSize: '13px', opacity: 0.95, fontWeight: '500' }}>Total Inferences Run</div>
                    <div style={{ fontSize: '42px', fontWeight: 'bold', marginTop: '5px' }}>
                        {status?.total_inferences_run || 0}
                    </div>
                </div>

                {/* Timing Info */}
                <div style={{ fontSize: '13px', color: '#e2e8f0', lineHeight: '1.6', padding: '8px 0' }}>
                    <p style={{ margin: '4px 0' }}><strong style={{ color: '#ffffff' }}>Last Inference:</strong> {formatTime(status?.last_inference_time)}</p>
                    <p style={{ margin: '4px 0' }}><strong style={{ color: '#ffffff' }}>Next Inference:</strong> {formatTime(status?.next_inference_time)}</p>
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