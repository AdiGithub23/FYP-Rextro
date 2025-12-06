# FYP Machine Condition UI - Setup Instructions

## Frontend Setup

### 1. Install Dependencies
```bash
cd FYP-Machine-Condition-UI/FYP-Machine-Condition-UI
npm install
```

### 2. Environment Configuration
The `.env` file is already configured with:
```
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start Development Server
```bash
npm run dev
```
The frontend will be available at `http://localhost:5173`

---

## Backend Setup (Already Done)

The backend `main.py` has been updated with CORS middleware to allow requests from the frontend.

### Start Backend Server
```bash
cd FYP-Machine-Condition-Prediction
python main.py
```
The backend API will be available at `http://localhost:8000`

---

## How It Works

### Data Flow:
1. **Real-time Data (Every 10 seconds):**
   - Frontend calls `/sensor/buffer` to get 160 historical points
   - Displayed as solid lines on the chart

2. **Forecast Data (Every 3 minutes):**
   - Frontend calls `/inference/last-prediction` to get 20 forecasted points
   - Displayed as dashed lines on the chart

3. **Chart Features:**
   - Select different sensors from dropdown (temp_body, temp_shaft, vibration_x, vibration_y, vibration_z, current)
   - Real-time data shown in solid lines
   - Forecasted data shown in dashed lines
   - Time-series x-axis with proper date/time formatting

### API Endpoints Used:
- `GET /sensor/buffer` - Returns 160 sensor data points
- `GET /inference/last-prediction` - Returns forecast array + alerts
- `GET /inference/status` - Returns inference status info

---

## Project Structure

```
src/
├── components/
│   ├── UnifiedSensorChart.jsx  # Main chart component (real-time + forecast)
│   ├── Dashboard.jsx            # Main dashboard layout
│   ├── AlertPanel.jsx           # Shows alerts from model
│   └── InferenceStatus.jsx      # Shows inference service status
├── hooks/
│   ├── useSensorData.js         # Fetches buffer data every 10s
│   └── useForecast.js           # Fetches forecast every 3min
├── services/
│   └── api.js                   # API calls to backend
├── utils/
│   └── chartConfig.js           # Chart.js configuration
└── App.jsx                      # Root component
```

---

## Troubleshooting

### CORS Errors
- Ensure backend `main.py` has CORS middleware configured
- Check that frontend is running on `http://localhost:5173`

### No Data Showing
- Verify backend is running: `http://localhost:8000/docs`
- Check InfluxDB is running and has data
- Open browser console to see API errors

### Chart Not Rendering
- Ensure all Chart.js dependencies are installed
- Check browser console for errors
- Verify data format matches expected structure

---

## Next Steps

1. Run `npm install` in the frontend directory
2. Start backend: `python main.py`
3. Start frontend: `npm run dev`
4. Open `http://localhost:5173` in browser
5. Select different sensors from dropdown to view data
