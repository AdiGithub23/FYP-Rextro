import React from 'react';

const AlertPanel = ({ alerts }) => {
    return (
        <div className="alert-panel">
            <h2>Alerts</h2>
            {alerts && alerts.length > 0 ? (
                <ul>
                    {alerts.map((alert, index) => (
                        <li key={index} className={`alert ${alert.status}`}>
                            {alert.message}
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No alerts at the moment.</p>
            )}
        </div>
    );
};

export default AlertPanel;