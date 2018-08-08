# CHOICES:
# - BROKER (local gateway) *Mondatory*
# - IBM (Watson IoT Platform)
# - SCP (Sap Cloud Platform NEO)
# - AWS (Amazon Web Services)
# - GCP (Google Cloud Platform)
CLIENTS = ["BROKER", "IBM"]
# END CONFIG


# PROGRAM
list = []

if "BROKER" in CLIENTS:
   list.append({
      "broker_name": "127.0.0.1",
      "certificate": "",
      "client_name": "raspberry_broker",
      "username": "mosquitto",
      "password": "mosquitto",
      "port": 1883,
      "transport": "tcp",
      "sub_topic": ["DHT11/temperature", "DHT11/humidity"],
      "pub_topic": "IN/instruction",
      "client_type": "gateway"
   })

if "IBM" in CLIENTS:
   try:
      from IBM import ibm_config as ibm
      list.append({
         "broker_name": ibm.org_id + ".messaging.internetofthings.ibmcloud.com",
         "client_name": "d:" + ibm.org_id + ":" + ibm.device_type + ":" + ibm.device_id,
         "port": ibm.port,
         "transport": "",
         "certificate": "",
         "username": ibm.auth_method,
         "password": ibm.auth_token,
         "sub_topic": ["iot-2/type/" + ibm.device_type + "/id/" + ibm.device_id + ibm.sub_topic],
         "pub_topic": "iot-2/type/" + ibm.device_type + "/id/" + ibm.device_id + ibm.pub_topic,
         "client_type": "IBM"
      })
   except ImportError:
      print("Please copy ibm_config_exemple.py to ibm_config.py and configure appropriately !");

if "SCP" in CLIENTS:
   try:
      from SCP import scp_config as scp
      list.append({
         "broker_name": "iotmms" + scp.scp_account_id + scp.scp_landscape_host,
         "endpoint_path": "/com.sap.iotservices.mms/v1/api/ws/mqtt",
         "certificate": scp.endpoint_certif,
         "client_name": scp.device_id,
         "username": scp.device_id,
         "password": scp.oauth_cred_device,
         "port": scp.port,
         "transport": scp.transport,
         "sub_topic": ["iot/push/" + scp.device_id],
         "pub_topic": "iot/data/" + scp.device_id,
         "instruction_message_type": scp.in_topic,
         "pushing_message_type": scp.out_topic,
         "client_type": "SCP"
      })
   except ImportError:
      print("Please copy scp_config_exemple.py to scp_config.py and configure appropriately !"); exit();

if "AWS" in CLIENTS:
   try:
      from AWS import aws_config as aws
      list.append({
         "broker_name": aws.endpoint,
         "certificate": aws.root_ca_path,
         "client_name": aws.client,
         "username": "",
         "password": "",
         "port": aws.port,
         "transport": aws.transport,
         "sub_topic": [aws.sub_topic],
         "pub_topic": aws.pub_topic,
         "client_type": "AWS"
      })
   except ImportError:
      print("Please copy aws_config_exemple.py to aws_config.py and configure appropriately !"); exit();

if "GCP" in CLIENTS:
   try:
      from GCP import gcp_config as gcp
      list.append({
         "broker_name": gcp.endpoint,
         "certificate": gcp.root_certificate,
         "client_name": 'projects/' + gcp.project_id + '/locations/' + gcp.cloud_region +'/registries/' + gcp.registry_id + '/devices/' + gcp.device_id,
         "private_key_file": gcp.private_key_file,
         "algorithm": gcp.algorithm,
         "port": gcp.port,
         "sub_topic": ["projects/" + gcp.project_id + "/topics/" + gcp.sub_topic],
         "pub_topic": "projects/" + gcp.project_id + "/topics/" + gcp.pub_topic,
         "client_type": "GCP"
      })
   except ImportError:
      print("Please copy gcp_config_exemple.py to gcp_config.py and configure appropriately !"); exit();
