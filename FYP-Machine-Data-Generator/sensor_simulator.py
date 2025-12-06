# python sensor_simulator.py

import csv
import time
import os
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision

# -------------------- CONFIGURATION --------------------
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "qtxWXZZTZEdD9DmlHnfOp-iQidzZE3oC1WpedxilZmlPYXTqAP3ofwxP9bCNq23OeNtpDSK5qzk3vB__Ln8HTg=="
INFLUX_ORG = "FYP"
INFLUX_BUCKET = "fyp"
MACHINE_ID = "68889e4d171eff841cba171a"
CSV_FILE = os.path.join(os.path.dirname(__file__), "datasets", "secondly_sensor_dataset.csv")
# --------------------------------------------------------

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api()

def read_csv_data(file_path):
    """Generator that yields rows from the CSV file one by one."""
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield {
                "current": float(row["current"]),
                "tempA": float(row["tempA"]),
                "tempB": float(row["tempB"]),
                "accX": float(row["accX"]),
                "accY": float(row["accY"]),
                "accZ": float(row["accZ"]),
            }

# Create generator for CSV data
csv_generator = read_csv_data(CSV_FILE)
row_count = 0
INITIAL_BATCH_SIZE = 230

print(f"📁 Reading sensor data from: {CSV_FILE}")
print(f"🚀 Sending first {INITIAL_BATCH_SIZE} data points at once...\n")

# Send the first 230 data points at once
initial_points = []
for i in range(INITIAL_BATCH_SIZE):
    try:
        data = next(csv_generator)
        row_count += 1
    except StopIteration:
        print(f"⚠️ CSV file has fewer than {INITIAL_BATCH_SIZE} rows. Sent {row_count} rows.")
        break
    
    print(f"[{datetime.now()}] Row {row_count} - Preparing Data: {data}")
    
    point = (
        Point("machine_metrics")
        .tag("machine_id", MACHINE_ID)
        .field("current", data["current"])
        .field("tempA", data["tempA"])
        .field("tempB", data["tempB"])
        .field("accX", data["accX"])
        .field("accY", data["accY"])
        .field("accZ", data["accZ"])
        .time(datetime.utcnow(), WritePrecision.NS)
    )
    initial_points.append(point)

# Write all initial points at once
if initial_points:
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=initial_points)
    print(f"\n✅ Successfully sent first {len(initial_points)} data points at once!")
    print(f"🚀 Now continuing to stream remaining data every 10 seconds...\n")

while True:
    try:
        data = next(csv_generator)
        row_count += 1
    except StopIteration:
        # Restart from the beginning of the CSV file
        print(f"\n🔄 Reached end of CSV file after {row_count} rows. Restarting from beginning...\n")
        csv_generator = read_csv_data(CSV_FILE)
        row_count = 1
        data = next(csv_generator)

    print(f"[{datetime.now()}] Row {row_count} - Sending Data: {data}")

    point = (
        Point("machine_metrics")
        .tag("machine_id", MACHINE_ID)
        .field("current", data["current"])
        .field("tempA", data["tempA"])
        .field("tempB", data["tempB"])
        .field("accX", data["accX"])
        .field("accY", data["accY"])
        .field("accZ", data["accZ"])
        .time(datetime.utcnow(), WritePrecision.NS)
    )

    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

    time.sleep(10)  # Send data every 10 seconds
