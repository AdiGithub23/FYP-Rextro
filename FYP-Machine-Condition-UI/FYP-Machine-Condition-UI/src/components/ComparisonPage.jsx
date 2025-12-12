import React from 'react';
import { useNavigate } from 'react-router-dom';
import ComparisonChart from './ComparisonChart';
import { FEATURE_NAMES, FEATURE_DISPLAY_NAMES } from '../utils/chartConfig';
import '../styles/index.css';

const ComparisonPage = () => {
    const navigate = useNavigate();

    return (
        <div className="dashboard-container">
            {/* Header with Back Button */}
            <header className="dashboard-header" style={{ background: '#1e293b', borderRadius: '12px', padding: '20px', textAlign: 'center', marginBottom: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <button 
                        onClick={() => navigate('/')}
                        style={{
                            background: '#334155',
                            color: '#f8fafc',
                            border: '1px solid #475569',
                            padding: '10px 20px',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: '600',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}
                    >
                        <span>←</span> Back to Dashboard
                    </button>
                    <div style={{ flex: 1, textAlign: 'center' }}>
                        <h1 style={{ color: '#ffffff', margin: 0 }}>Last Inference Validation</h1>
                        <p style={{ color: '#f8fafc', marginTop: '5px', opacity: 0.9, fontSize: '14px' }}>
                            Validate last inference: Compare predicted vs actual data for the most recent 60 points
                        </p>
                    </div>
                    <div style={{ width: '150px' }}></div> {/* Spacer for centering */}
                </div>
            </header>

            {/* Info Banner */}
            <div style={{
                background: '#1e293b',
                border: '2px solid #3b82f6',
                borderRadius: '10px',
                padding: '15px 20px',
                marginBottom: '20px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
            }}>
                <span style={{ fontSize: '20px' }}>ℹ️</span>
                <div style={{ color: '#e2e8f0', fontSize: '14px', lineHeight: '1.5' }}>
                    <strong style={{ color: '#ffffff' }}>How to read these charts:</strong>
                    <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
                        <li><strong style={{ color: '#ffffff' }}>Solid line (Actual Data):</strong> Real sensor data from the last 60 points</li>
                        <li><strong style={{ color: '#ffffff' }}>Dashed line (Predicted Data):</strong> What the model predicted for these same 60 points in the previous inference run</li>
                        <li style={{ marginTop: '8px', color: '#22c55e' }}>✅ <em>Direct comparison: The closer the dashed line matches the solid line, the more accurate the prediction!</em></li>
                        <li style={{ marginTop: '4px', color: '#94a3b8' }}>📊 <em>This view focuses only on validating the last inference accuracy (60 points window)</em></li>
                    </ul>
                </div>
            </div>

            {/* Charts Grid - All 6 Features with Comparison */}
            <div className="charts-section" style={{ background: '#1e293b', padding: '20px', borderRadius: '12px', marginBottom: '20px' }}>
                <h2 style={{ marginBottom: '15px', color: '#ffffff', fontWeight: 'bold' }}>
                    All Sensors - Last 60 Points Validation
                </h2>
                <div className="charts-grid">
                    {FEATURE_NAMES.map(feature => (
                        <div key={feature} className="chart-card">
                            <ComparisonChart selectedFeature={feature} />
                        </div>
                    ))}
                </div>
            </div>

            {/* Footer */}
            <footer className="dashboard-footer" style={{ background: '#1e293b', padding: '15px', borderRadius: '10px', textAlign: 'center' }}>
                <p style={{ color: '#e2e8f0' }}>
                    Use this page to analyze model performance by comparing predictions vs actual outcomes
                </p>
            </footer>
        </div>
    );
};

export default ComparisonPage;
