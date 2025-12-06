import time
from influxdb_client import InfluxDBClient
from datetime import datetime

# ---------------- CONFIG ----------------
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "qtxWXZZTZEdD9DmlHnfOp-iQidzZE3oC1WpedxilZmlPYXTqAP3ofwxP9bCNq23OeNtpDSK5qzk3vB__Ln8HTg=="
INFLUX_ORG = "FYP"
INFLUX_BUCKET = "fyp"
MACHINE_ID = "68889e4d171eff841cba171a"
# ----------------------------------------

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()

print("\n🔍 Listening for real-time grouped data...\n")

last_time = None

while True:
    timestamp_query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -2m)
      |> filter(fn: (r) => r._measurement == "machine_metrics")
      |> filter(fn: (r) => r.machine_id == "{MACHINE_ID}")
      |> keep(columns: ["_time"])
      |> sort(columns: ["_time"], desc: true)
      |> limit(n:1)
    '''

    timestamp_result = query_api.query(timestamp_query)

    latest_time = None
    for table in timestamp_result:
        for record in table.records:
            latest_time = record.get_time()

    if latest_time and latest_time != last_time:
        full_query = f'''
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: -5m)
          |> filter(fn: (r) => r["_measurement"] == "machine_metrics")
          |> filter(fn: (r) => r["machine_id"] == "{MACHINE_ID}")
          |> pivot(
              rowKey:["_time"],
              columnKey: ["_field"],
              valueColumn: "_value"
          )
          |> sort(columns: ["_time"], desc: false)
        '''

        full_data = query_api.query(full_query)

        for table in full_data:
            for record in table.records:
                if record["_time"] == latest_time:   # Get only matching timestamp row
                    print(f"\n[{datetime.now()}] New Full Sensor Record:")
                    print(f"Time: {latest_time}")
                    print(f"Machine ID: {MACHINE_ID}")
                    print(f"temp_body: {record.values.get('temp_body')}")
                    print(f"temp_shaft: {record.values.get('temp_shaft')}")
                    print(f"vibration_x: {record.values.get('vibration_x')}")
                    print(f"vibration_y: {record.values.get('vibration_y')}")
                    print(f"vibration_z: {record.values.get('vibration_z')}")
                    print(f"current: {record.values.get('current')}")

        last_time = latest_time

    time.sleep(10)
