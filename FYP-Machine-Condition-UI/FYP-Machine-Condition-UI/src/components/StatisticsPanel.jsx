import React from 'react';

const StatisticsPanel = ({ statistics }) => {
    return (
        <div className="statistics-panel">
            <h2>Statistics</h2>
            <ul>
                {statistics.map((stat, index) => (
                    <li key={index}>
                        <strong>{stat.label}:</strong> {stat.value}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default StatisticsPanel;