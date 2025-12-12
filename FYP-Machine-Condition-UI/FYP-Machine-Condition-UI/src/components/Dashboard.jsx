import React from 'react';
import { useNavigate } from 'react-router-dom';
import UnifiedSensorChart from './UnifiedSensorChart';
import AnomalyScorePanel from './AnomalyScorePanel';
import InferenceStatus from './InferenceStatus';
import useForecast from '../hooks/useForecast';
import { FEATURE_NAMES, FEATURE_DISPLAY_NAMES } from '../utils/chartConfig';
import '../styles/index.css';

const Dashboard = () => {
    const { alerts, metadata, loading } = useForecast();
    const navigate = useNavigate();

    // Generate alert message based on status
    const getAlertDisplay = () => {
        if (!alerts || !alerts.message) {
            return {
                message: 'Waiting for first inference cycle...',
                status: 'info',
                icon: '⏳',
                criticalFeatures: []
            };
        }
        
        if (alerts.status === 'critical') {
            return {
                message: alerts.message,
                status: 'critical',
                icon: '🚨',
                criticalFeatures: alerts.critical_features || []
            };
        }
        
        if (alerts.status === 'warning') {
            return {
                message: alerts.message,
                status: 'warning',
                icon: '⚠️',
                criticalFeatures: []
            };
        }
        
        return {
            message: alerts.message,
            status: 'normal',
            // icon: '✅',
            icon: '',
            criticalFeatures: []
        };
    };

    const alertDisplay = getAlertDisplay();

    return (
        <div className="dashboard-container">
            {/* Header */}
            <header className="dashboard-header" style={{ background: '#1e293b', borderRadius: '12px', padding: '20px', textAlign: 'center', marginBottom: '20px' }}>
                <h1 style={{ color: '#ffffff' }}>Machine Condition Monitoring Dashboard</h1>
                <p style={{ color: '#f8fafc', marginTop: '5px', opacity: 0.9 }}>
                    Real-time PatchTST Inference • Lookback: 240 points • Forecast: 60 points
                </p>
            </header>

            {/* Main Alert Banner */}
            <div className={`alert-banner alert-${alertDisplay.status}`} style={{ background: '#1e293b', border: '2px solid #334155', padding: '15px 20px', borderRadius: '10px', marginBottom: '20px' }}>
                <span className="alert-icon">{alertDisplay.icon}</span>
                <div className="alert-content">
                    <span className="alert-message">{alertDisplay.message}</span>
                    
                    {/* Display critical features if machine is at risk */}
                    {alertDisplay.criticalFeatures && alertDisplay.criticalFeatures.length > 0 && (
                        <div className="critical-features-list">
                            <strong>🎯 Focus on these sensors:</strong>
                            {' '}
                            {alertDisplay.criticalFeatures.map((feature, idx) => (
                                <span key={feature} className="critical-feature-badge">
                                    {FEATURE_DISPLAY_NAMES[feature] || feature}
                                    {idx < alertDisplay.criticalFeatures.length - 1 && ', '}
                                </span>
                            ))}
                        </div>
                    )}
                </div>
                {metadata?.inference_count > 0 && (
                    <span className="inference-badge">
                        Inference #{metadata.inference_count}
                    </span>
                )}
            </div>

            {/* Top Row: Status and Anomaly Scores */}
            <div className="top-panels">
                <div className="status-panel">
                    <InferenceStatus />
                </div>
                <div className="anomaly-panel">
                    <AnomalyScorePanel alerts={alerts} />
                </div>
            </div>

            {/* Charts Grid - All 6 Features */}
            <div className="charts-section" style={{ background: '#1e293b', padding: '20px', borderRadius: '12px', marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                    <h2 style={{ margin: 0, color: '#ffffff', fontWeight: 'bold' }}>
                        Sensor Data & Forecasts
                    </h2>
                    <button 
                        onClick={() => navigate('/comparison')}
                        style={{
                            background: '#3b82f6',
                            color: '#ffffff',
                            border: 'none',
                            padding: '10px 20px',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: '600',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            transition: 'background 0.2s'
                        }}
                        onMouseEnter={(e) => e.target.style.background = '#2563eb'}
                        onMouseLeave={(e) => e.target.style.background = '#3b82f6'}
                    >
                        📊 Comparison
                    </button>
                </div>
                <div className="charts-grid">
                    {FEATURE_NAMES.map(feature => (
                        <div key={feature} className="chart-card">
                            <UnifiedSensorChart selectedFeature={feature} />
                        </div>
                    ))}
                </div>
            </div>

            {/* Footer */}
            <footer className="dashboard-footer" style={{ background: '#1e293b', padding: '15px', borderRadius: '10px', textAlign: 'center' }}>
                <p style={{ color: '#e2e8f0' }}>
                    Last updated: {metadata?.timestamp ? new Date(metadata.timestamp).toLocaleString() : 'N/A'}
                    {' | '}
                    Total Inferences: {metadata?.inference_count || 0}
                </p>
            </footer>
        </div>
    );
};

export default Dashboard;