try: from config import config
except ImportError: print("Please fill the config file and configure appropriately !"); exit();

CL = {
   "CLOUD_SCP": "SCP",
   "CLOUD_IBM": "IBM",
   "CLOUD_AWS": "AWS",
   "CLOUD_GCP": "GCP",
   "CLOUD_CCF": "SCF",
   "CLOUD_AZR": "AZR"
}

CLIENTS = config.CLIENTS
list = []

def sub_topics(sensors):
   topics = []
   for i in range(len(sensors)):
      for j in range(len(config.SENSORS[i]["pub_topics"])):
         topics.append(config.SENSORS[i]["name"] + "/" + config.SENSORS[i]["pub_topics"][j])
   return topics

if "BROKER" in CLIENTS:
   list.append({
      "broker_name": "127.0.0.1",
      "certificate": "",
      "client_name": "raspberry_broker",
      "username": "mosquitto",
      "password": "mosquitto",
      "port": 1883,
      "ssl": False,
      "transport": "tcp",
      "sub_topic": sub_topics(config.SENSORS),
      "pub_topic": "IN/instruction",
      "client_type": "gateway"
   })

if "IBM" in CLIENTS:
   try:
      from config.cloud.IBM import ibm_config as ibm
      list.append({
         "broker_name": ibm.org_id + ".messaging.internetofthings.ibmcloud.com",
         "client_name": "d:" + ibm.org_id + ":" + ibm.device_type + ":" + ibm.device_id,
         "port": ibm.port,
         "transport": "",
         "certificate": "",
         "ssl": ibm.ssl,
         "username": ibm.auth_method,
         "password": ibm.auth_token,
         "sub_topic": ["iot-2/type/" + ibm.device_type + "/id/" + ibm.device_id + ibm.sub_topic],
         "pub_topic": "iot-2/type/" + ibm.device_type + "/id/" + ibm.device_id + ibm.pub_topic,
         "client_type": CL["CLOUD_IBM"]
      })
   except ImportError:
      print("Please copy ibm_config_exemple.py to ibm_config.py and configure appropriately !");

if "SCP" in CLIENTS:
   try:
      from config.cloud.SCP import scp_config as scp
      list.append({
         "broker_name": "iotmms" + scp.scp_account_id + scp.scp_landscape_host,
         "endpoint_path": "/com.sap.iotservices.mms/v1/api/ws/mqtt",
         "certificate": scp.endpoint_certif,
         "client_name": scp.device_id,
         "username": scp.device_id,
         "password": scp.oauth_cred_device,
         "port": scp.port,
         "ssl": scp.ssl,
         "transport": scp.transport,
         "sub_topic": ["iot/push/" + scp.device_id],
         "pub_topic": "iot/data/" + scp.device_id,
         "instruction_message_type": scp.in_topic,
         "pushing_message_type": scp.out_topic,
         "client_type": CL["CLOUD_SCP"]
      })
   except ImportError:
      print("Please copy scp_config_exemple.py to scp_config.py and configure appropriately !"); exit();

if "AWS" in CLIENTS:
   try:
      from config.cloud.AWS import aws_config as aws
      list.append({
         "broker_name": aws.endpoint,
         "certificate": aws.root_ca_path,
         "device_cert": aws.device_ca_path,
         "key_path": aws.key_path,
         "public_key": aws.public_key,
         "client_name": aws.client,
         "username": "",
         "password": "",
         "port": aws.port,
         "ssl": aws.ssl,
         "transport": aws.transport,
         "sub_topic": [aws.sub_topic],
         "pub_topic": aws.pub_topic,
         "client_type": CL["CLOUD_AWS"]
      })
   except ImportError:
      print("Please copy aws_config_exemple.py to aws_config.py and configure appropriately !"); exit();

if "GCP" in CLIENTS:
   try:
      from config.cloud.GCP import gcp_config as gcp
      list.append({
         "broker_name": gcp.endpoint,
         "certificate": gcp.root_certificate,
         "client_name": 'projects/' + gcp.project_id + '/locations/' + gcp.cloud_region +'/registries/' + gcp.registry_id + '/devices/' + gcp.device_id,
         "private_key_file": gcp.private_key_file,
         "algorithm": gcp.algorithm,
         "port": gcp.port,
         "ssl": gcp.ssl,
         "sub_topic": ["projects/" + gcp.project_id + "/topics/" + gcp.sub_topic],
         "pub_topic": "projects/" + gcp.project_id + "/topics/" + gcp.pub_topic,
         "client_type": CL["CLOUD_GCP"]
      })
   except ImportError:
      print("Please copy gcp_config_exemple.py to gcp_config.py and configure appropriately !"); exit();
