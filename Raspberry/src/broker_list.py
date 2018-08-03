try:
   from AWS import aws_config as aws
except ImportError:
   print("Please copy aws_config_exemple.py to aws_config.py and configure appropriately !"); exit();

try:
   from SCP import scp_config as scp
except ImportError:
   print("Please copy scp_config_exemple.py to scp_config.py and configure appropriately !"); exit();

list = [{
   "broker_name": aws.endpoint,
   "certificate": aws.root_ca_path,
   "client_name": aws.client,
   "username": "",
   "password": "",
   "port": 443,
   "transport": "websockets",
   "sub_topic": ["AWS/instruction"],
   "pub_topic": "AWS/DHT11Data",
   "client_type": "AWS"
}, {
   "broker_name": "iotmms" + scp.scp_account_id + scp.scp_landscape_host,
   "endpoint_path": "/com.sap.iotservices.mms/v1/api/ws/mqtt",
   "certificate": scp.endpoint_certificate,
   "client_name": scp.device_id,
   "username": scp.device_id,
   "password": scp.oauth_credentials_for_device,
   "port": 443,
   "transport": "websockets",
   "sub_topic": ["iot/push/" + scp.device_id],
   "pub_topic": "iot/data/" + scp.device_id,
   "instruction_message_type": scp.in_topic,
   "pushing_message_type": scp.out_topic,
   "client_type": "SCP"
}, {
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
}]

