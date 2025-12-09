from datetime import datetime
import os
import pickle
from matplotlib.style import context
import numpy as np
import torch
from scipy.signal import butter, filtfilt
from transformers import PatchTSTForPrediction


class InferenceService:
    def __init__(self):
        """
        Initialize the inference service with model and scaler.
        Configured for X-std model artifacts with context_length=240, prediction_length=60
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # base_dir = os.path.join(current_dir, "..", "AI-Model-Artifacts", "X-std")
        base_dir = os.path.join(current_dir, "..", "AI-Model-Artifacts", "CustomLoss")
        base_dir = os.path.abspath(base_dir)
        
        self.model_path = os.path.join(base_dir, "patchtst_sensor_multivar")
        self.scaler_path = os.path.join(base_dir, "scaler.pkl")
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Model configuration matching notebook: context=240, prediction=60
        self.context_length = 240
        self.prediction_length = 60
        self.num_features = 6
        
        # Feature names matching the model training order
        self.feature_names = ['current', 'tempA', 'tempB', 'accX', 'accY', 'accZ']
        
        # Load scaler
        print(f"[InferenceService] Loading scaler from: {self.scaler_path}")
        try:
            with open(self.scaler_path, "rb") as f:
                self.scaler = pickle.load(f)
            print("✅ Scaler loaded successfully")
        except FileNotFoundError:
            print(f"⚠️ Scaler not found at: {self.scaler_path}")
            print(f"   Running WITHOUT scaling (using raw data directly)")
            self.scaler = None
        except Exception as e:
            print(f"❌ Error loading scaler: {e}")
            print(f"   Running WITHOUT scaling (using raw data directly)")
            self.scaler = None
        
        # Load model using HuggingFace's from_pretrained (as shown in notebook)
        print(f"[InferenceService] Loading model from: {self.model_path}")
        try:
            self.model = PatchTSTForPrediction.from_pretrained(
                self.model_path, 
                local_files_only=True
            )
            self.model.to(self.device)
            self.model.eval()
            print(f"✅ Model loaded successfully on {self.device}")
            print(f"   Parameters: {sum(p.numel() for p in self.model.parameters()):,}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise

    def apply_butterworth_filter(self, data, cutoff=0.1, order=2):
        """
        Apply Butterworth low-pass filter to smooth sensor data.
        
        Args:
            data (np.ndarray): Input data of shape (n_samples, n_features)
            cutoff (float): Normalized cutoff frequency (0 to 1)
            order (int): Filter order
        
        Returns:
            np.ndarray: Filtered data
        """
        b, a = butter(order, cutoff, btype='low', analog=False)
        filtered_data = np.zeros_like(data)
        
        for i in range(data.shape[1]):
            filtered_data[:, i] = filtfilt(b, a, data[:, i])
        
        return filtered_data

    def run_inference(self, buffer_data):
        """
        Simplified inference pipeline: Raw data → Butterworth → StandardScaler → Model → Raw predictions
        
        Args:
            buffer_data (list of dicts): 240 data points from InfluxDB
                Each dict contains: timestamp, current, tempA, tempB, accX, accY, accZ, machine_id
        
        Returns:
            results (dict): Contains raw model predictions in scaled space
            alerts (dict): Status and message
        """
        print("\n" + "="*80)
        print("[InferenceService] Starting Simplified Inference Pipeline")
        print("="*80)
        
        # Validate input
        if len(buffer_data) != self.context_length:
            error_msg = f"Expected {self.context_length} data points, got {len(buffer_data)}"
            print(f"❌ {error_msg}")
            return None, {"status": "error", "message": error_msg}
        
        try:
            # ============================================================
            # STEP 1: Extract raw features from buffer
            # ============================================================
            print(f"\n[Step 1] Extracting raw features from buffer...")
            raw_data = np.array([
                [
                    point['current'],
                    point['tempA'],
                    point['tempB'],
                    point['accX'],
                    point['accY'],
                    point['accZ']
                ]
                for point in buffer_data
            ], dtype=np.float32)
            
            print(f"✅ Raw data extracted, shape: {raw_data.shape}")
            print(f"\n   First 5 data points (raw):")
            for step in range(min(5, raw_data.shape[0])):
                values = ", ".join([f"{self.feature_names[i]}={raw_data[step, i]:.4f}" 
                                  for i in range(self.num_features)])
                print(f"     Point {step+1}: {values}")
            
            # ============================================================
            # STEP 2: Apply Butterworth filter (smoothing)
            # ============================================================
            print(f"\n[Step 2] Applying Butterworth filter for smoothing (cutoff=0.3, order=2)...")
            smoothed_data = self.apply_butterworth_filter(raw_data, cutoff=0.3, order=2)
            
            print(f"✅ Data smoothed, shape: {smoothed_data.shape}")
            print(f"\n   First 5 data points (after Butterworth filter):")
            for step in range(min(5, smoothed_data.shape[0])):
                values = ", ".join([f"{self.feature_names[i]}={smoothed_data[step, i]:.4f}" 
                                  for i in range(self.num_features)])
                print(f"     Point {step+1}: {values}")
            
            # ============================================================
            # STEP 3: Apply StandardScaler transform
            # ============================================================
            if self.scaler is not None:
                print(f"\n[Step 3] Applying StandardScaler transform...")
                scaled_input = self.scaler.transform(smoothed_data).astype(np.float32)
                print(f"✅ Data scaled, shape: {scaled_input.shape}")
            else:
                print(f"\n[Step 3] ⚠️ Scaler not available, using raw data directly...")
                scaled_input = smoothed_data.astype(np.float32)
                print(f"✅ Using raw data, shape: {scaled_input.shape}")
    
            print(f"\n   First 5 data points (after StandardScaler):")
            for step in range(min(5, scaled_input.shape[0])):
                values = ", ".join([f"{self.feature_names[i]}={scaled_input[step, i]:+.4f}" 
                                  for i in range(self.num_features)])
                print(f"     Point {step+1}: {values}")
            
            # ============================================================
            # STEP 4: Prepare tensor and run model inference
            # ============================================================
            print(f"\n[Step 4] Running model inference...")
            model_input = scaled_input.reshape(1, self.context_length, self.num_features)
            input_tensor = torch.tensor(model_input, dtype=torch.float32).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(past_values=input_tensor)
                preds = outputs.prediction_outputs
                
                if isinstance(preds, tuple):
                    preds = preds[0]
                
                raw_predictions = preds.squeeze(0).cpu().numpy()
            
            print(f"✅ Model inference complete, prediction shape: {raw_predictions.shape}")
            print(f"\n   First 5 predictions (raw model output in scaled space):")
            for step in range(min(5, raw_predictions.shape[0])):
                values = ", ".join([f"{self.feature_names[i]}={raw_predictions[step, i]:+.4f}" 
                                  for i in range(self.num_features)])
                print(f"     Step {step+1}: {values}")
            
            # ============================================================
            # STEP 5: POST-PROCESSING TRICK - FIT PREDICTIONS TO LOOKBACK SCALE
            # ============================================================
            print(f"\n[Step 5] Applying post-processing trick to fit predictions into lookback scale...")
            
            # 5a: Remove outliers from raw predictions
            print(f"\n   5a. Removing outliers from raw predictions (threshold=3.0)...")
            pred_no_outliers = self._remove_prediction_outliers(raw_predictions, threshold=3.0)
            
            # 5b: Scale predictions to match input context (preserving first 3 predictions)
            print(f"\n   5b. Preserving first 3 predictions, scaling remaining 57 to SCALED input context...")
            first_3_predictions = pred_no_outliers[:3, :]  # Keep outlier-removed values as-is
            rest_57_predictions = pred_no_outliers[3:, :]  # Scale these to match context
            
            # Scale only the last 57 points
            scaled_57 = self._scale_predictions_to_context(rest_57_predictions, scaled_input, method='minmax')
            
            # Concatenate: first 3 (preserved) + 57 (scaled)
            final_predictions = np.vstack([first_3_predictions, scaled_57])
            print(f"✅ First 3 predictions preserved in scaled space (outlier-removed only)")
            
            print(f"✅ Post-processing complete, final prediction shape: {final_predictions.shape}")
            print(f"\n   First 5 predictions (final model output fitted to SCALED input range):")
            for step in range(min(5, final_predictions.shape[0])):
                values = ", ".join([f"{self.feature_names[i]}={final_predictions[step, i]:.4f}" 
                                  for i in range(self.num_features)])
                print(f"     Step {step+1}: {values}")
            
            # ============================================================
            # STEP 6: ANOMALY DETECTION
            # ============================================================
            print(f"\n[Step 6] Calculating anomaly scores...")
            
            # Inverse transform final predictions to get raw sensor values
            if self.scaler is not None:
                predictions_raw = self.scaler.inverse_transform(final_predictions)
            else:
                predictions_raw = final_predictions
            
            # Calculate anomaly scores based on predefined thresholds
            anomaly_results = self._calculate_anomaly_scores(predictions_raw)
            
            # ============================================================
            # RESULTS: Return both raw and final predictions
            # ============================================================
            results = {
                "raw_predictions_scaled": raw_predictions,
                "final_predictions": final_predictions,
                "input_context_scaled": scaled_input,
                "input_context_raw": raw_data
            }
            
            # Original alerts (commented for reference):
            # alerts = {
            #     "status": "success",
            #     "message": "Inference completed successfully with post-processing",
            #     "timestamp": datetime.now().isoformat()
            # }
            
            # New alerts with anomaly detection:
            alerts = {
                "status": "critical" if anomaly_results["machine_at_risk"] else "normal",
                "message": anomaly_results["message"],
                "timestamp": datetime.now().isoformat(),
                "anomaly_scores": anomaly_results["scores"],
                "critical_features": anomaly_results["critical_features"],
                "machine_id": buffer_data[0].get('machine_id', 'Unknown')  # Extract machine_id from buffer data
            }
            
            print("\n" + "="*80)
            print("[InferenceService] Inference Pipeline Complete")
            print("="*80)
            
            return results, alerts
        
        except Exception as e:
            error_msg = f"Error during inference: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return None, {"status": "error", "message": error_msg}
    
    def _remove_prediction_outliers(self, predictions, threshold=3.0):
        """
        Remove/replace outliers in predictions using Z-score method.
        
        Args:
            predictions (np.ndarray): Model predictions (60, 6)
            threshold (float): Z-score threshold for outlier detection
        
        Returns:
            np.ndarray: Predictions with outliers replaced by interpolated values
        """
        cleaned = predictions.copy()
        
        for i in range(predictions.shape[1]):
            col = predictions[:, i]
            
            # Calculate Z-scores
            mean = np.mean(col)
            std = np.std(col)
            
            if std > 1e-8:
                z_scores = np.abs((col - mean) / std)
                outlier_mask = z_scores > threshold
                num_outliers = np.sum(outlier_mask)
                
                if num_outliers > 0:
                    # Replace outliers with interpolated values
                    col_cleaned = col.copy()
                    col_cleaned[outlier_mask] = np.nan
                    
                    # Linear interpolation
                    nans = np.isnan(col_cleaned)
                    x = np.arange(len(col_cleaned))
                    
                    if np.sum(~nans) >= 2:  # Need at least 2 points for interpolation
                        col_cleaned[nans] = np.interp(x[nans], x[~nans], col_cleaned[~nans])
                    else:
                        col_cleaned[nans] = mean
                    
                    cleaned[:, i] = col_cleaned
                    print(f"       {self.feature_names[i]}: {num_outliers} outliers removed")
                else:
                    print(f"       {self.feature_names[i]}: No outliers detected")
            else:
                print(f"       {self.feature_names[i]}: No outliers detected (std too small)")
        
        return cleaned
    
    def _scale_predictions_to_context(self, predictions, context, method='robust'):
        """
        Scale predictions to match the statistical properties of the input context.
        
        Args:
            predictions (np.ndarray): Model predictions (60, 6)
            context (np.ndarray): Input context window (240, 6) - SCALED data
            method (str): 'minmax', 'robust', or 'zscore'
        
        Returns:
            np.ndarray: Predictions scaled to match context statistics
        """
        scaled = np.zeros_like(predictions)
        num_features = predictions.shape[1]
    
        # Use only last 15% of context
        last_x_percent = int(context.shape[0] * 0.15)
        recent_context = context[-last_x_percent:, :]

        print(f"       Using last {last_x_percent} points ({last_x_percent}/{context.shape[0]}) for scaling range")
    
        
        for i in range(num_features):
            pred_col = predictions[:, i]
            ctx_col = recent_context[:, i]
            
            if method == 'minmax':
                # Min-max scaling to context range
                # Use percentiles to stretch predictions and avoid clustering
                pred_min = np.percentile(pred_col, 5)   # 5th percentile (ignore bottom 5%)
                pred_max = np.percentile(pred_col, 95)  # 95th percentile (ignore top 5%)
                
                # Fallback to actual min/max if percentiles are too close (predictions are very uniform)
                if (pred_max - pred_min) < 1e-8:
                    pred_min = pred_col.min()
                    pred_max = pred_col.max()
                
                # Original method (commented for reference):
                # pred_min = pred_col.min()
                # pred_max = pred_col.max()
                
                ctx_min = ctx_col.min()
                ctx_max = ctx_col.max()
                
                if (pred_max - pred_min) > 1e-8:
                    # Normalize predictions to [0, 1] using percentiles
                    normalized = (pred_col - pred_min) / (pred_max - pred_min)
                    # Scale to context range
                    scaled[:, i] = normalized * (ctx_max - ctx_min) + ctx_min
                else:
                    # If predictions are constant, use context midpoint
                    scaled[:, i] = np.full_like(pred_col, (ctx_max + ctx_min) / 2)
                
                print(f"       {self.feature_names[i]}: scaled from [{pred_min:.4f}, {pred_max:.4f}] (5th-95th percentile) to [{ctx_min:.4f}, {ctx_max:.4f}]")
            
            elif method == 'robust':
                # Robust scaling using median and IQR
                pred_median = np.median(pred_col)
                pred_iqr = np.percentile(pred_col, 75) - np.percentile(pred_col, 25)
                ctx_median = np.median(ctx_col)
                ctx_iqr = np.percentile(ctx_col, 75) - np.percentile(ctx_col, 25)
                
                if pred_iqr > 1e-8:
                    robust_scaled = (pred_col - pred_median) / pred_iqr
                    scaled[:, i] = robust_scaled * ctx_iqr + ctx_median
                else:
                    scaled[:, i] = np.full_like(pred_col, ctx_median)
                
                print(f"       {self.feature_names[i]}: scaled using robust statistics")
            
            elif method == 'zscore':
                # Z-score scaling: match mean and std
                pred_mean = pred_col.mean()
                pred_std = pred_col.std()
                ctx_mean = ctx_col.mean()
                ctx_std = ctx_col.std()
                
                if pred_std > 1e-8:
                    standardized = (pred_col - pred_mean) / pred_std
                    scaled[:, i] = standardized * ctx_std + ctx_mean
                else:
                    scaled[:, i] = np.full_like(pred_col, ctx_mean)
                
                print(f"       {self.feature_names[i]}: scaled using z-score")
        
        return scaled
    
    def _calculate_anomaly_scores(self, predictions_raw):
        """
        Calculate anomaly scores for each feature based on predefined thresholds.
        
        Thresholds:
        - tempA/tempB: > 45°C
        - current: > 11A
        - accX: < -1.9 or > 0.7
        - accY: < -2.0 or > 0.7
        - accZ: < 5.5 or > 14.5
        
        Machine is at risk if ANY feature exceeds threshold in ≥30% of predictions (18/60 points).
        
        Args:
            predictions_raw (np.ndarray): Predictions in original sensor units (60, 6)
        
        Returns:
            dict: {
                "machine_at_risk": bool,
                "message": str,
                "scores": dict,
                "critical_features": list
            }
        """
        # Define thresholds for each feature
        thresholds = {
            'current': {'max': 11.0},
            'tempA': {'max': 45.0},
            'tempB': {'max': 45.0},
            'accX': {'min': -1.9, 'max': 0.7},
            'accY': {'min': -2.0, 'max': 0.7},
            'accZ': {'min': 5.5, 'max': 14.5}
        }
        
        num_predictions = predictions_raw.shape[0]  # 60
        critical_threshold_percentage = 30.0  # 30% = 18 points
        
        scores = {}
        critical_features = []
        
        print(f"\n   Anomaly Detection Results:")
        
        for i, feature in enumerate(self.feature_names):
            feature_values = predictions_raw[:, i]
            threshold = thresholds[feature]
            
            # Count points exceeding threshold
            exceeding_count = 0
            
            if 'min' in threshold and 'max' in threshold:
                # Range check (accX, accY, accZ)
                exceeding_count = np.sum((feature_values < threshold['min']) | (feature_values > threshold['max']))
            elif 'max' in threshold:
                # Upper limit only (current, tempA, tempB)
                exceeding_count = np.sum(feature_values > threshold['max'])
            
            # Calculate percentage
            percentage = (exceeding_count / num_predictions) * 100
            scores[feature] = round(percentage, 2)
            
            # Check if critical
            is_critical = percentage >= critical_threshold_percentage
            if is_critical:
                critical_features.append(feature)
            
            # Print result
            status_icon = "⚠️ CRITICAL" if is_critical else "✅ Normal"
            print(f"       {feature:10s}: {exceeding_count}/{num_predictions} points exceed threshold ({percentage:.2f}%) {status_icon}")
        
        # Determine overall machine status
        machine_at_risk = len(critical_features) > 0
        
        if machine_at_risk:
            critical_list = ", ".join([f"{feat} ({scores[feat]:.2f}%)" for feat in critical_features])
            message = f"⚠️ Machine condition at risk. Critical features: {critical_list}"
            print(f"\n   {message}")
        else:
            message = "✅ Machine condition normal. All features within acceptable ranges."
            print(f"\n   {message}")
        
        return {
            "machine_at_risk": machine_at_risk,
            "message": message,
            "scores": scores,
            "critical_features": critical_features
        }
