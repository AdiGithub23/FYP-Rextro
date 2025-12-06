### 01. Influx DB (Real time data coming in 10-second intervals)

### 02. Get every data point via GET Method

### 03. Collect 240 data points into a temporary buffer (Initially, load the available last 240 data points at once)

### 04. Now consider these 240 data points as the last lookback which should be given to the model as input

### 05. Model Inference:
```
	- Existing Data Preprocessing Pipeline
	- Feed the preprocessed data into the Model
	- Get the Model Output
	- Fit the raw model output into the model input scale (window lookback scale)
	- Inverse scale everything back to the original sensor reading ranges using the saved scaler.pkl
	- Apply Tolerance Band Logic
```

### 06. Anomaly Detection - Percentage in which the model output horizon data points are exceeding the predefined healthy boundary for each sensor feature

### 07. If the Anomaly Score Percentage >= 30%? Machine Condition at Risk: Machine Condition Normal

### 08. If Machine Condition at Risk? (Machine Condition at Risk) Return a Generated Alert + Email: (Machine Condition Normal) Return a Generated Alert

### 09. If Machine Condition at Risk? (Machine Condition at Risk) Specifically mention as because of which sensor features the condition is at risk

### 10. Repeat this every 180 seconds (3 minutes)