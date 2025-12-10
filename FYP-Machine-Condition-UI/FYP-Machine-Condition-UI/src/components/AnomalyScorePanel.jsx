import React from 'react';
import { FEATURE_DISPLAY_NAMES } from '../utils/chartConfig';

const AnomalyScorePanel = ({ alerts }) => {
    // Original code (commented for reference):
    // const featureDetails = alerts?.feature_details || {};
    // const atRiskFeatures = alerts?.at_risk_features || [];
    
    // Updated to match backend structure:
    const anomalyScores = alerts?.anomaly_scores || {};
    const criticalFeatures = alerts?.critical_features || [];
    
    // Get all features from the scores
    const features = Object.keys(anomalyScores);
    
    const getScoreColor = (percentage) => {
        if (percentage >= 30) return '#ff3b30'; // Red - At Risk
        if (percentage >= 15) return '#ff9500'; // Orange - Warning
        return '#00ff88'; // Green - Normal
    };

    const getScoreBackground = (percentage) => {
        if (percentage >= 30) return 'rgba(255, 59, 48, 0.15)';
        if (percentage >= 15) return 'rgba(255, 149, 0, 0.15)';
        return 'rgba(0, 255, 136, 0.15)';
    };

    if (!features.length) {
        return (
            <div className="panel" style={{ background: '#1e293b' }}>
                <h3 style={{ fontSize: '18px', color: '#ffffff' }}>📊 Anomaly Scores</h3>
                <p style={{ color: '#e2e8f0', fontStyle: 'italic', fontSize: '14px' }}>
                    Waiting for first inference cycle...
                </p>
            </div>
        );
    }

    return (
        <div className="panel" style={{ background: '#1e293b' }}>
            <h3 style={{ marginBottom: '15px', fontSize: '18px', color: '#ffffff', fontWeight: 'bold' }}>Anomaly Scores by Feature</h3>
            <p style={{ fontSize: '13px', color: '#e2e8f0', marginBottom: '15px', fontWeight: '500' }}>
                Threshold: 30% (values above trigger alert)
            </p>
            
            <div style={{ display: 'grid', gap: '10px' }}>
                {features.map(feature => {
                    // Original code (commented for reference):
                    // const details = featureDetails[feature];
                    // const percentage = details?.anomaly_percentage || 0;
                    // const isAtRisk = atRiskFeatures.includes(feature);
                    
                    // Updated to match backend structure:
                    const percentage = anomalyScores[feature] || 0;
                    const isAtRisk = criticalFeatures.includes(feature);
                    
                    return (
                        <div 
                            key={feature}
                            style={{
                                padding: '12px',
                                borderRadius: '8px',
                                background: getScoreBackground(percentage),
                                border: `2px solid ${getScoreColor(percentage)}`,
                            }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div>
                                    <strong style={{ fontSize: '15px', color: '#f8fafc' }}>
                                        {FEATURE_DISPLAY_NAMES[feature] || feature}
                                    </strong>
                                    {isAtRisk && (
                                        <span style={{ 
                                            marginLeft: '8px', 
                                            padding: '3px 8px', 
                                            background: '#ff3b30', 
                                            color: 'white', 
                                            borderRadius: '4px',
                                            fontSize: '11px',
                                            fontWeight: 'bold',
                                            boxShadow: '0 0 8px rgba(255, 59, 48, 0.5)'
                                        }}>
                                            AT RISK
                                        </span>
                                    )}
                                </div>
                                <span style={{ 
                                    fontSize: '20px', 
                                    fontWeight: 'bold',
                                    color: getScoreColor(percentage)
                                }}>
                                    {percentage.toFixed(1)}%
                                </span>
                            </div>
                            
                            {/* Progress bar */}
                            <div style={{ 
                                marginTop: '8px', 
                                height: '8px', 
                                background: '#0f1419', 
                                border: '1px solid #2d3748',
                                borderRadius: '4px',
                                overflow: 'hidden'
                            }}>
                                <div style={{
                                    width: `${Math.min(percentage, 100)}%`,
                                    height: '100%',
                                    background: getScoreColor(percentage),
                                    boxShadow: `0 0 8px ${getScoreColor(percentage)}`,
                                    transition: 'width 0.3s ease'
                                }} />
                            </div>
                            
                            {/* Original detail counts (commented - backend doesn't provide these): */}
                            {/* <div style={{ 
                                marginTop: '6px', 
                                fontSize: '11px', 
                                color: '#666',
                                display: 'flex',
                                justifyContent: 'space-between'
                            }}>
                                <span>Above max: {details?.exceeding_max || 0}</span>
                                <span>Below min: {details?.below_min || 0}</span>
                            </div> */}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default AnomalyScorePanel;
