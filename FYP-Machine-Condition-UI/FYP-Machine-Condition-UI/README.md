# FYP-Machine-Condition-UI

This project is a frontend application built with React and Vite that visualizes real-time data from InfluxDB and forecasted model outputs. The application integrates various components to provide a comprehensive dashboard for monitoring machine conditions.

## Project Structure

- **public/**: Contains static assets like the Vite logo.
- **src/**: The main source code for the application.
  - **assets/**: Contains image assets such as the React logo.
  - **components/**: Contains React components for the dashboard, charts, alerts, and statistics.
  - **services/**: Contains API service functions for fetching data from the backend.
  - **hooks/**: Custom hooks for managing state and data fetching.
  - **utils/**: Utility functions and configurations for charts and data transformation.
  - **styles/**: Global styles for the application.
  - **App.jsx**: Main application component that sets up routing and renders the dashboard.
  - **main.jsx**: Entry point of the application.

## Features

- **Real-Time Data Visualization**: Displays live sensor data from InfluxDB.
- **Forecast Visualization**: Shows forecasted model outputs on the same graph as real-time data.
- **Alerts**: Displays alerts based on inference results.
- **Statistics**: Provides statistical data related to sensor readings.
- **Inference Status**: Displays the current status of the inference process.

## Getting Started

1. Clone the repository:
   ```
   git clone <repository-url>
   cd FYP-Machine-Condition-UI
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env` and configure the necessary variables.

4. Start the development server:
   ```
   npm run dev
   ```

5. Open your browser and navigate to `http://localhost:3000` to view the application.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or features.

## License

This project is licensed under the MIT License. See the LICENSE file for details.