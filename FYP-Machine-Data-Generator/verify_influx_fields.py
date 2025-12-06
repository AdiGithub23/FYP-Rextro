# python verify_influx_fields.py
# This script verifies what field names are actually stored in InfluxDB

from influxdb_client import InfluxDBClient

# ---------------- CONFIG ----------------
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "qtxWXZZTZEdD9DmlHnfOp-iQidzZE3oC1WpedxilZmlPYXTqAP3ofwxP9bCNq23OeNtpDSK5qzk3vB__Ln8HTg=="
INFLUX_ORG = "FYP"
INFLUX_BUCKET = "fyp"
MACHINE_ID = "68889e4d171eff841cba171a"
# ----------------------------------------

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()

print("=" * 60)
print("VERIFYING INFLUXDB FIELD NAMES")
print("=" * 60)

# Query to get the latest record with all fields
query = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -10m)
  |> filter(fn: (r) => r["_measurement"] == "machine_metrics")
  |> filter(fn: (r) => r["machine_id"] == "{MACHINE_ID}")
  |> pivot(
      rowKey:["_time"],
      columnKey: ["_field"],
      valueColumn: "_value"
  )
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
'''

result = query_api.query(query)

print("\n📊 CSV File Headers:")
print("   current, tempA, tempB, accX, accY, accZ")

print("\n🗄️  InfluxDB Field Names Found:")
for table in result:
    for record in table.records:
        print(f"\n   Time: {record.get_time()}")
        print(f"   Machine ID: {record.values.get('machine_id')}")
        print(f"\n   All available fields in this record:")
        
        # Get all keys from record.values, excluding metadata
        field_keys = [k for k in record.values.keys() 
                     if not k.startswith('_') and k != 'result' 
                     and k != 'table' and k != 'machine_id']
        
        print(f"   Fields: {field_keys}")
        print(f"\n   Field values:")
        for field in field_keys:
            print(f"   - {field}: {record.values.get(field)}")

print("\n" + "=" * 60)
print("✅ MATCH?" if set(['current', 'tempA', 'tempB', 'accX', 'accY', 'accZ']).issubset(field_keys if 'field_keys' in locals() else []) else "❌ MISMATCH DETECTED")
print("=" * 60)

client.close()
