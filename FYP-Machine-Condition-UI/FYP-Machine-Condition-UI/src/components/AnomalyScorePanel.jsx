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
        if (percentage >= 30) return '#dc3545'; // Red - At Risk
        if (percentage >= 15) return '#ffc107'; // Yellow - Warning
        return '#28a745'; // Green - Normal
    };

    const getScoreBackground = (percentage) => {
        if (percentage >= 30) return 'rgba(220, 53, 69, 0.1)';
        if (percentage >= 15) return 'rgba(255, 193, 7, 0.1)';
        return 'rgba(40, 167, 69, 0.1)';
    };

    if (!features.length) {
        return (
            <div className="panel">
                <h3>📊 Anomaly Scores</h3>
                <p style={{ color: '#666', fontStyle: 'italic' }}>
                    Waiting for first inference cycle...
                </p>
            </div>
        );
    }

    return (
        <div className="panel">
            <h3 style={{ marginBottom: '15px' }}>Anomaly Scores by Feature</h3>
            <p style={{ fontSize: '12px', color: '#666', marginBottom: '15px' }}>
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
                                    <strong style={{ fontSize: '14px' }}>
                                        {FEATURE_DISPLAY_NAMES[feature] || feature}
                                    </strong>
                                    {isAtRisk && (
                                        <span style={{ 
                                            marginLeft: '8px', 
                                            padding: '2px 6px', 
                                            background: '#dc3545', 
                                            color: 'white', 
                                            borderRadius: '4px',
                                            fontSize: '10px',
                                            fontWeight: 'bold'
                                        }}>
                                            AT RISK
                                        </span>
                                    )}
                                </div>
                                <span style={{ 
                                    fontSize: '18px', 
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
                                background: '#e9ecef', 
                                borderRadius: '4px',
                                overflow: 'hidden'
                            }}>
                                <div style={{
                                    width: `${Math.min(percentage, 100)}%`,
                                    height: '100%',
                                    background: getScoreColor(percentage),
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
