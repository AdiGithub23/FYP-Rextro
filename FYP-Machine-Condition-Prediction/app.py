# python main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.real_influx_streamer_4 import ScheduledInfluxInference
import threading

app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure streamer with:
# - Data collection every 10 seconds into rolling buffer
# - Inference every 3 minutes (180 seconds) using last 240 points
# - Predicts next 60 data points
streamer = ScheduledInfluxInference(
    inference_interval_seconds=180,  # 3 minutes
    data_collection_interval_seconds=10  # Collect data every 10 seconds
)


@app.get("/sensor/means-history-db")
def get_means_history_from_db():
    """
    Return recent mean values from MongoDB.
    TEMPORARILY DISABLED FOR TERMINAL-ONLY TESTING
    """
    return {"status": "disabled", "message": "Frontend endpoints disabled for testing"}
    # data = streamer.get_recent_means_from_db()
    # return {
    #     "status": "success",
    #     "means_collected": len(data),
    #     "data": data
    # }

@app.on_event("startup")
def start_background_inference():
    """
    Start the scheduled inference process in the background.
    Runs inference every 3 minutes automatically.
    """
    thread = threading.Thread(target=streamer.start_stream, daemon=True)
    thread.start()
    print("Background inference scheduler started (runs every 3 minutes).")

@app.get("/inference/last-prediction")
def get_last_prediction():
    """
    Get the most recent prediction results including:
    - Raw forecast (direct model output in scaled space)
    - Scaled forecast (fitted to scaled input range)
    - Alerts and anomaly detection results
    """
    prediction_data = streamer.get_last_prediction()
    
    if prediction_data is None:
        return {
            "status": "error",
            "message": "No predictions available yet. Wait for first inference cycle.",
            "raw_forecast": None,
            "scaled_forecast": None,
            "alerts": None
        }
    
    # Generate future timestamps for forecast (matching data collection interval)
    import datetime
    last_lookback = streamer.get_last_lookback()
    data_interval = streamer.data_collection_interval  # 10 seconds
    if last_lookback and len(last_lookback) > 0:
        last_timestamp = datetime.datetime.fromisoformat(last_lookback[-1]['timestamp'].replace('Z', '+00:00'))
        future_timestamps = [
            (last_timestamp + datetime.timedelta(seconds=data_interval * (i + 1))).isoformat()
            for i in range(60)  # 60 prediction steps
        ]
    else:
        future_timestamps = None
    
    # Format scaled forecast (predictions in scaled space fitted to input range)
    scaled_forecast_array = prediction_data["scaled_forecast"]
    
    # Apply inverse scaling to convert from scaled space to raw sensor values
    if streamer.inference_service.scaler is not None:
        forecast_raw = streamer.inference_service.scaler.inverse_transform(scaled_forecast_array)
    else:
        print(f"⚠️ [API] Scaler not available, using predictions without inverse transform")
        forecast_raw = scaled_forecast_array
    
    scaled_forecast_formatted = {
        "predictions": [
            {
                "step": i + 1,
                "timestamp": future_timestamps[i] if future_timestamps else None,
                "current": float(forecast_raw[i, 0]),
                "tempA": float(forecast_raw[i, 1]),
                "tempB": float(forecast_raw[i, 2]),
                "accX": float(forecast_raw[i, 3]),
                "accY": float(forecast_raw[i, 4]),
                "accZ": float(forecast_raw[i, 5])
            }
            for i in range(forecast_raw.shape[0])
        ],
        "forecast_horizon": forecast_raw.shape[0],
        "num_features": forecast_raw.shape[1]
    }
    
    return {
        "status": "success",
        "message": "Last prediction retrieved successfully",
        "inference_count": prediction_data["inference_count"],
        "timestamp": prediction_data["timestamp"],
        "alerts": prediction_data["alerts"],
        "scaled_forecast": scaled_forecast_formatted,
        "scaled_forecast_array": scaled_forecast_array.tolist(),
        "raw_forecast_array": prediction_data["raw_forecast"].tolist()
    }
    #     "raw_forecast": raw_forecast_formatted,
    #     "scaled_forecast": scaled_forecast_formatted,
    #     "raw_forecast_array": prediction_data["raw_forecast"].tolist(),
    #     "scaled_forecast_array": prediction_data["scaled_forecast"].tolist()
@app.get("/inference/status")
def get_inference_status():
    """
    Get the status of the inference scheduler including timing information.
    """
    status_data = streamer.get_inference_status()
    return {
        "status": "success",
        "data": status_data
    }

@app.get("/sensor/latest")
def get_latest_sensor_point():
    """
    Return the most recent datapoint.
    TEMPORARILY DISABLED FOR TERMINAL-ONLY TESTING
    """
    return {"status": "disabled", "message": "Frontend endpoints disabled for testing"}
    # data = streamer.get_latest_point()
    # if data is None:
    #     return {
    #         "status": "error",
    #         "msg": "No data available yet. Wait for first inference cycle.",
    #         "data": None
    #     }
    # return {
    #     "status": "success",
    #     "msg": "Latest data retrieved successfully",
    #     "data": data
    # }

@app.get("/sensor/buffer")
def get_buffer_data():
    """
    Return all data points in the buffer (last 160 points).
    TEMPORARILY DISABLED FOR TERMINAL-ONLY TESTING
    """
    return {"status": "disabled", "message": "Frontend endpoints disabled for testing"}
    # data = streamer.get_buffer()
    # return {
    #     "status": "success",
    #     "points_collected": len(data),
    #     "data": data
    # }


@app.get("/sensor/history")
def get_last_hour_points():
    """TEMPORARILY DISABLED FOR TERMINAL-ONLY TESTING"""
    return {"status": "disabled", "message": "Frontend endpoints disabled for testing"}
    # data = streamer.get_last_360_points()
    # return {
    #     "status": "success",
    #     "points_collected": len(data),
    #     "data": data
    # }

@app.get("/sensor/hourly-mean")
def get_hourly_mean():
    """TEMPORARILY DISABLED FOR TERMINAL-ONLY TESTING"""
    return {"status": "disabled", "message": "Frontend endpoints disabled for testing"}

@app.get("/sensor/means-history")
def get_means_history():
    """
    Return the list of automatically calculated mean values.
    TEMPORARILY DISABLED FOR TERMINAL-ONLY TESTING
    """
    return {"status": "disabled", "message": "Frontend endpoints disabled for testing"}
    # return {
    #     "status": "success",
    #     "means_collected": len(streamer.get_means_list()),
    #     "data": streamer.get_means_list()
    # }

@app.get("/sensor/last-lookback")
def get_last_lookback():
    """
    Retrieve the last 240 data points used for inference (lookback window).
    """
    data = streamer.get_last_lookback()
    return {
        "status": "success",
        "points_collected": len(data),
        "data": data
    }

@app.get("/inference/previous-forecast")
def get_previous_forecast():
    """
    Retrieve the forecast from the previous inference run.
    This can be overlaid with the last 60 lookback points to show prediction accuracy.
    
    Returns:
        - previous_forecast: 60 points x 6 features array from previous inference
        - null if no previous forecast exists yet
    """
    previous_forecast = streamer.get_previous_forecast()
    
    if previous_forecast is None:
        return {
            "status": "success",
            "has_previous_forecast": False,
            "message": "No previous forecast available yet (need at least 2 inference runs)",
            "previous_forecast": None
        }
    
    # Convert numpy array to list of dicts for JSON serialization
    forecast_list = []
    feature_names = ["current", "tempA", "tempB", "accX", "accY", "accZ"]
    
    for i in range(len(previous_forecast)):
        point = {
            "index": i,
            "current": float(previous_forecast[i][0]),
            "tempA": float(previous_forecast[i][1]),
            "tempB": float(previous_forecast[i][2]),
            "accX": float(previous_forecast[i][3]),
            "accY": float(previous_forecast[i][4]),
            "accZ": float(previous_forecast[i][5])
        }
        forecast_list.append(point)
    
    return {
        "status": "success",
        "has_previous_forecast": True,
        "points_predicted": len(forecast_list),
        "previous_forecast": forecast_list
    }





