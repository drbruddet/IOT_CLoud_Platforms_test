# CLIENT LIST:
# - BROKER (local gateway) *Mandatory*
# - IBM (Watson IoT Platform)
# - SCP (Sap Cloud Platform NEO)
# - SCF (Sap Cloud Platform Cloud Foundry)
# - AWS (Amazon Web Services)
# - GCP (Google Cloud Platform)
CLIENTS = ["BROKER", "AWS"]

# SENSOR LIST CONFIG:
SENSORS = [{
   "name": "DHT11",
   "instruction": "DHT11",
   "data": [0, 0],
   "pub_topics": ["temperature", "humidity"]
}]
