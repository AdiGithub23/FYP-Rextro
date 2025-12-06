# services/real_influx_streamer_4.py
import time
from datetime import datetime
from collections import deque
import threading
from influxdb_client import InfluxDBClient
from services.inference_service_3 import InferenceService
from services.email_service import EmailNotificationService
from configs.mongodb_config import influx_url, influx_token, influx_org, influx_bucket, workspace_id


class ScheduledInfluxInference:
    def __init__(self, inference_interval_seconds=180, data_collection_interval_seconds=1):
        """
        Initialize scheduled inference service with continuous data collection.
        
        - Collects sensor data every second into a rolling buffer
        - Runs inference every N seconds (default: 180 = 3 minutes)
        - Uses last 240 data points for model input (context window)
        - Predicts next 60 data points (forecast horizon)
        
        Args:
            inference_interval_seconds (int): Time between inference runs (default: 180 seconds = 3 minutes)
            data_collection_interval_seconds (int): Interval for data collection (default: 1 second)
        """
        self.influx_client = InfluxDBClient(
            url=influx_url, 
            token=influx_token, 
            org=influx_org
        )
        self.influx_bucket = influx_bucket
        self.workspace_id = workspace_id
        
        self.inference_interval = inference_interval_seconds
        self.data_collection_interval = data_collection_interval_seconds
        
        # Configuration matching the X-std model
        self.context_length = 240  # Lookback window
        self.prediction_length = 60  # Forecast horizon
        
        # Rolling buffer to store continuous data (keep extra for safety)
        self.buffer_max_size = self.context_length + 100  # 340 points max
        self.data_buffer = deque(maxlen=self.buffer_max_size)
        
        # Prediction storage
        self.last_prediction = None
        self.last_alerts = None
        self.last_lookback = []
        self.last_raw_forecast = None
        self.last_scaled_forecast = None
        self.next_inference_time = None
        self.inference_count = 0
        
        # Thread control
        self.running = False
        self.data_collection_thread = None
        self.inference_thread = None
        
        # Initialize inference service
        print(f"[ScheduledInflux] Initializing inference service...")
        self.inference_service = InferenceService()
        
        # Initialize email notification service
        print(f"[ScheduledInflux] Initializing email notification service...")
        self.email_service = EmailNotificationService()
        
        print(f"[ScheduledInflux] Configuration:")
        print(f"   - Data collection: every {data_collection_interval_seconds} second(s)")
        print(f"   - Inference: every {inference_interval_seconds} seconds ({inference_interval_seconds/60:.1f} minutes)")
        print(f"   - Context window: {self.context_length} points")
        print(f"   - Forecast horizon: {self.prediction_length} points")

    def start_stream(self):
        """
        Start both data collection and inference loops.
        
        On startup:
        1. Immediately fetch last 240 data points from InfluxDB (for fast testing)
        
        Data Collection (runs every 10 seconds):
        1. Query latest data point from InfluxDB
        2. Append to rolling buffer
        
        Inference (runs every 3 minutes):
        1. Take last 240 points from buffer
        2. Scale using scaler.pkl
        3. Run model inference
        4. Print raw output
        5. Scale output to match lookback context
        6. Print final scaled output
        """
        print("\n" + "="*80)
        print("[ScheduledInflux] Starting Scheduled Inference System")
        print("="*80)
        
        self.running = True
        
        # IMMEDIATELY fetch last 240 points from InfluxDB to avoid waiting
        print(f"\n[ScheduledInflux] Fetching last {self.context_length} points from InfluxDB...")
        initial_data = self._query_last_n_points(self.context_length)
        if initial_data and len(initial_data) > 0:
            self.data_buffer.clear()
            for point in initial_data:
                self.data_buffer.append(point)
            print(f"✅ [ScheduledInflux] Buffer pre-filled with {len(self.data_buffer)} points")
        else:
            print(f"⚠️ [ScheduledInflux] Could not fetch initial data, will collect gradually")
        
        # Start data collection thread (continues to add new points)
        self.data_collection_thread = threading.Thread(
            target=self._data_collection_loop, 
            daemon=True
        )
        self.data_collection_thread.start()
        print("[ScheduledInflux] Data collection thread started")
        
        # Run inference loop in main thread
        self._inference_loop()

    def _data_collection_loop(self):
        """
        Continuously refresh buffer with last 240 points from InfluxDB.
        This ensures inference is always ready with the most recent data.
        """
        print(f"\n[DataCollection] Starting continuous buffer refresh (fetching last 240 points every {self.data_collection_interval}s)...")
        
        refresh_count = 0
        while self.running:
            try:
                # Fetch last 240 points from InfluxDB
                last_240 = self._query_last_n_points(self.context_length)
                
                if last_240 and len(last_240) >= self.context_length:
                    # Replace entire buffer with fresh data
                    self.data_buffer.clear()
                    for point in last_240:
                        self.data_buffer.append(point)
                    
                    refresh_count += 1
                    # Log every 10 cycles to reduce spam (every 100 seconds)
                    if refresh_count % 10 == 0:
                        print(f"[DataCollection] Buffer refreshed: {len(self.data_buffer)} points (refresh #{refresh_count})")
                elif last_240:
                    print(f"⚠️ [DataCollection] Only {len(last_240)}/{self.context_length} points available in InfluxDB")
                else:
                    print(f"⚠️ [DataCollection] No data returned from InfluxDB")
                
                time.sleep(self.data_collection_interval)
                
            except Exception as e:
                print(f"❌ [DataCollection] Error: {e}")
                time.sleep(self.data_collection_interval)

    # DEPRECATED: No longer used - buffer now refreshed with _query_last_n_points()
    # def _query_latest_point(self):
    #     """
    #     Query InfluxDB for the most recent data point.
    #     
    #     Returns:
    #         dict: Single data point with sensor values, or None if error
    #     """
    #     query = f'''
    #     from(bucket: "{self.influx_bucket}")
    #       |> range(start: -1m)
    #       |> filter(fn: (r) => r["_measurement"] == "machine_metrics")
    #       |> filter(fn: (r) => r["machine_id"] == "{self.workspace_id}")
    #       |> pivot(
    #           rowKey: ["_time"],
    #           columnKey: ["_field"],
    #           valueColumn: "_value"
    #       )
    #       |> sort(columns: ["_time"], desc: true)
    #       |> limit(n: 1)
    #     '''
    #     
    #     try:
    #         result = self.influx_client.query_api().query(query)
    #         
    #         for table in result:
    #             for record in table.records:
    #                 try:
    #                     return {
    #                         "timestamp": record.get_time().isoformat(),
    #                         "current": float(record.values.get("current", 0) or 0),
    #                         "tempA": float(record.values.get("tempA", 0) or 0),
    #                         "tempB": float(record.values.get("tempB", 0) or 0),
    #                         "accX": float(record.values.get("accX", 0) or 0),
    #                         "accY": float(record.values.get("accY", 0) or 0),
    #                         "accZ": float(record.values.get("accZ", 0) or 0),
    #                         "machine_id": self.workspace_id,
    #                     }
    #                 except (TypeError, ValueError) as e:
    #                     print(f"❌ [DataCollection] Error converting values: {e}")
    #                     return None
    #         
    #         return None
    #         
    #     except Exception as e:
    #         print(f"❌ [DataCollection] Error querying InfluxDB: {e}")
    #         return None

    def _inference_loop(self):
        """
        Run inference every N seconds using the last 240 points from buffer.
        """
        print(f"\n[Inference] Starting inference loop (every {self.inference_interval}s)...")
        
        while self.running:
            try:
                self.next_inference_time = datetime.now()
                next_time_str = self.next_inference_time.strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"\n{'='*80}")
                print(f"[Inference] Inference #{self.inference_count + 1} at {next_time_str}")
                print(f"{'='*80}")
                
                # Check if we have enough data
                buffer_size = len(self.data_buffer)
                print(f"[Inference] Buffer size: {buffer_size}/{self.context_length} points")
                
                if buffer_size < self.context_length:
                    print(f"⚠️ [Inference] Insufficient data: {buffer_size}/{self.context_length} points")
                    print(f"   Need {self.context_length - buffer_size} more points")
                    print(f"   Estimated time: ~{(self.context_length - buffer_size) * self.data_collection_interval}s")
                    
                    # Try to backfill from InfluxDB
                    print(f"[Inference] Attempting to backfill from InfluxDB...")
                    backfill_data = self._query_last_n_points(self.context_length)
                    
                    if backfill_data and len(backfill_data) >= self.context_length:
                        self.data_buffer.clear()
                        for point in backfill_data:
                            self.data_buffer.append(point)
                        print(f"✅ [Inference] Backfilled buffer with {len(self.data_buffer)} points")
                    else:
                        print(f"[Inference] Waiting {self.inference_interval}s before retry...")
                        time.sleep(self.inference_interval)
                        continue
                
                # Get last 240 points from buffer
                buffer_list = list(self.data_buffer)
                last_240_points = buffer_list[-self.context_length:]
                
                print(f"✅ [Inference] Using last {len(last_240_points)} data points")
                print(f"   Time range: {last_240_points[0]['timestamp']} to {last_240_points[-1]['timestamp']}")
                
                # Store lookback for API access
                self.last_lookback = last_240_points.copy()
                
                # Run inference
                print(f"\n[Inference] Running model inference...")
                results, alerts = self.inference_service.run_inference(last_240_points)
                
                if results is not None:
                    # Store results
                    self.last_prediction = results
                    self.last_alerts = alerts
                    self.last_raw_forecast = results["raw_predictions_scaled"]  # Raw model output in scaled space
                    self.last_scaled_forecast = results["final_predictions"]  # Post-processed predictions fitted to lookback
                    self.inference_count += 1
                    
                    # Print both raw and final outputs
                    print(f"\n{'='*80}")
                    print("[OUTPUT] RAW MODEL OUTPUT (Scaled Space):")
                    print(f"{'='*80}")
                    self._print_forecast(results["raw_predictions_scaled"], "Raw Model Predictions")
                    
                    print(f"\n{'='*80}")
                    print("[OUTPUT] FINAL PREDICTIONS (Fitted to Lookback Scale):")
                    print(f"{'='*80}")
                    self._print_forecast(results["final_predictions"], "Final Model Predictions")
                    
                    print(f"\n✅ [Inference] Completed successfully")
                    print(f"   Alert status: {alerts['status']}")
                    print(f"   Alert message: {alerts['message']}")
                    
                    # ============================================================
                    # EMAIL NOTIFICATION: Send email after inference
                    # ============================================================
                    print(f"\n[Inference] Sending email notification...")
                    try:
                        if alerts.get('status') == 'critical':
                            print(f"[Inference] Machine status is CRITICAL, sending notification...")
                            email_sent = self.email_service.send_alert_email(
                                alert_data=alerts,
                                inference_count=self.inference_count
                            )
                        else:
                            print(f"[Inference] Machine status is {alerts.get('status')}, skipping email (only send for critical)")
                            email_sent = False
                        
                        if email_sent:
                            print(f"✅ [Inference] Email notification sent successfully")
                        else:
                            print(f"⚠️ [Inference] Email notification failed (check logs above)")
                    except Exception as email_error:
                        print(f"❌ [Inference] Error sending email: {email_error}")
                        # Don't stop the inference loop if email fails
                        import traceback
                        traceback.print_exc()
                    # ============================================================
                    
                else:
                    print(f"❌ [Inference] Failed: {alerts['message']}")
                
                # Wait for next inference cycle
                print(f"\n[Inference] Next inference in {self.inference_interval}s ({self.inference_interval/60:.1f} min)...")
                print(f"{'='*80}")
                time.sleep(self.inference_interval)
                
            except Exception as e:
                print(f"❌ [Inference] Error in inference loop: {e}")
                import traceback
                traceback.print_exc()
                print(f"[Inference] Retrying in {self.inference_interval}s...")
                time.sleep(self.inference_interval)

    def _print_forecast(self, forecast, label):
        """Print forecast values in a readable format."""
        feature_names = ['current', 'tempA', 'tempB', 'accX', 'accY', 'accZ']
        
        print(f"\n{label} - First 5 steps:")
        for step in range(min(5, forecast.shape[0])):
            values = ", ".join([f"{feature_names[i]}={forecast[step, i]:.4f}" 
                              for i in range(forecast.shape[1])])
            print(f"   Step {step+1}: {values}")
        
        print(f"\n{label} - Last 5 steps:")
        for step in range(max(0, forecast.shape[0]-5), forecast.shape[0]):
            values = ", ".join([f"{feature_names[i]}={forecast[step, i]:.4f}" 
                              for i in range(forecast.shape[1])])
            print(f"   Step {step+1}: {values}")
        
        print(f"\n{label} - Statistics:")
        for i, name in enumerate(feature_names):
            col = forecast[:, i]
            print(f"   {name:10s}: mean={col.mean():.4f}, min={col.min():.4f}, max={col.max():.4f}")

    def _query_last_n_points(self, n):
        """
        Query InfluxDB for the last N data points.
        
        Args:
            n (int): Number of points to query
            
        Returns:
            list: List of data points, or None if error
        """
        # Query range - use a large range to ensure we get enough data
        # Data is collected every 10 seconds, so 240 points = 40 minutes
        # Use 2 hours (120 minutes) to be safe
        range_minutes = max(120, (n * 15) // 60)  # Extra margin for 10-second intervals
        
        query = f'''
        from(bucket: "{self.influx_bucket}")
          |> range(start: -{range_minutes}m)
          |> filter(fn: (r) => r["_measurement"] == "machine_metrics")
          |> filter(fn: (r) => r["machine_id"] == "{self.workspace_id}")
          |> pivot(
              rowKey: ["_time"],
              columnKey: ["_field"],
              valueColumn: "_value"
          )
          |> sort(columns: ["_time"], desc: false)
          |> tail(n: {n})
        '''
        
        try:
            result = self.influx_client.query_api().query(query)
            data_points = []
            
            for table in result:
                for record in table.records:
                    # DEBUG: Print first record's fields
                    if len(data_points) == 0:
                        print(f"[DEBUG] First record fields: {list(record.values.keys())}")
                        print(f"[DEBUG] First record values: {record.values}")
                    
                    # InfluxDB already has correct field names: tempA, tempB, accX, accY, accZ
                    # No mapping needed
                    try:
                        data_point = {
                            "timestamp": record.get_time().isoformat(),
                            "current": float(record.values.get("current", 0) or 0),
                            "tempA": float(record.values.get("tempA", 0) or 0),
                            "tempB": float(record.values.get("tempB", 0) or 0),
                            "accX": float(record.values.get("accX", 0) or 0),
                            "accY": float(record.values.get("accY", 0) or 0),
                            "accZ": float(record.values.get("accZ", 0) or 0),
                            "machine_id": self.workspace_id,
                        }
                        data_points.append(data_point)
                    except (TypeError, ValueError) as e:
                        print(f"❌ [Inference] Error converting record values: {e}")
                        print(f"   Problematic record: {record.values}")
                        continue
            
            print(f"[Inference] Query returned {len(data_points)} data points")
            
            if len(data_points) == 0:
                print(f"⚠️ [Inference] No data found in last {range_minutes} minutes")
                print(f"   Check if data is being written to InfluxDB")
                print(f"   Measurement: 'machine_metrics'")
                print(f"   Machine ID: '{self.workspace_id}'")
            
            return data_points if len(data_points) > 0 else None
            
        except Exception as e:
            print(f"❌ [Inference] Error querying InfluxDB: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_last_prediction(self):
        """
        Get the most recent prediction results.
        
        Returns:
            dict: Contains raw and scaled forecasts, alerts, or None if no prediction yet
        """
        if self.last_prediction is None:
            return None
        
        return {
            "raw_forecast": self.last_raw_forecast,
            "scaled_forecast": self.last_scaled_forecast,
            "alerts": self.last_alerts,
            "inference_count": self.inference_count,
            "timestamp": self.last_alerts.get("timestamp") if self.last_alerts else None
        }
    
    def get_inference_status(self):
        """
        Get the status of the inference scheduler.
        
        Returns:
            dict: Status information including timing and buffer size
        """
        return {
            "status": "running" if self.running else "stopped",
            "inference_interval_seconds": self.inference_interval,
            "inference_interval_minutes": self.inference_interval / 60,
            "data_collection_interval_seconds": self.data_collection_interval,
            "context_length": self.context_length,
            "prediction_length": self.prediction_length,
            "buffer_size": len(self.data_buffer),
            "buffer_ready": len(self.data_buffer) >= self.context_length,
            "total_inferences_run": self.inference_count,
            "last_inference_time": self.last_alerts.get("timestamp") if self.last_alerts else None,
            "next_inference_time": self.next_inference_time.isoformat() if self.next_inference_time else None,
            "has_prediction": self.last_prediction is not None
        }
    
    def get_last_lookback(self):
        """
        Return the last 240 data points used for inference.
        
        Returns:
            list: Last lookback data (240 points)
        """
        return self.last_lookback
    
    def get_buffer(self):
        """
        Return all data points currently in the buffer.
        
        Returns:
            list: Current buffer data
        """
        return list(self.data_buffer)
    
    def get_latest_point(self):
        """
        Return the most recent data point from the buffer.
        
        Returns:
            dict: Most recent data point, or None if buffer empty
        """
        if len(self.data_buffer) > 0:
            return self.data_buffer[-1]
        return None

    def get_last_360_points(self):
        """
        Return up to the last 360 points from buffer (for compatibility).
        
        Returns:
            list: Last 360 data points
        """
        buffer_list = list(self.data_buffer)
        return buffer_list[-360:] if len(buffer_list) >= 360 else buffer_list

    def get_means_list(self):
        """
        Placeholder for compatibility with existing API.
        
        Returns:
            list: Empty list (means calculation not implemented in this version)
        """
        return []

    def get_recent_means_from_db(self):
        """
        Placeholder for compatibility with existing API.
        
        Returns:
            list: Empty list (MongoDB means not implemented in this version)
        """
        return []
