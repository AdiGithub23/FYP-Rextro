import React from 'react';
import UnifiedSensorChart from './UnifiedSensorChart';
import AnomalyScorePanel from './AnomalyScorePanel';
import InferenceStatus from './InferenceStatus';
import useForecast from '../hooks/useForecast';
import { FEATURE_NAMES, FEATURE_DISPLAY_NAMES } from '../utils/chartConfig';
import '../styles/index.css';

const Dashboard = () => {
    const { alerts, metadata, loading } = useForecast();

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
            <header className="dashboard-header">
                <h1>Machine Condition Monitoring Dashboard</h1>
                <p style={{ color: '#666', marginTop: '5px' }}>
                    Real-time PatchTST Inference • Lookback: 240 points • Forecast: 60 points
                </p>
            </header>

            {/* Main Alert Banner */}
            <div className={`alert-banner alert-${alertDisplay.status}`}>
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
            <div className="charts-section">
                <h2 style={{ marginBottom: '15px', color: '#333' }}>
                    Sensor Data & Forecasts
                </h2>
                <div className="charts-grid">
                    {FEATURE_NAMES.map(feature => (
                        <div key={feature} className="chart-card">
                            <UnifiedSensorChart selectedFeature={feature} />
                        </div>
                    ))}
                </div>
            </div>

            {/* Footer */}
            <footer className="dashboard-footer">
                <p>
                    Last updated: {metadata?.timestamp ? new Date(metadata.timestamp).toLocaleString() : 'N/A'}
                    {' | '}
                    Total Inferences: {metadata?.inference_count || 0}
                </p>
            </footer>
        </div>
    );
};

export default Dashboard;