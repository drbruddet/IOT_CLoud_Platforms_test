#!/usr/bin/python
# -*- coding: latin-1 -*-

import time, sys, threading, datetime, ssl
import paho.mqtt.client as mqtt
import jwt
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from concurrent import futures

try:
   import broker_list as broker
except ImportError:
   print("Please fill the broker_list.py and configure appropriately !"); exit();

# Application Config
"""CLOUD DECLARATION"""
CLOUD_SCP = "SCP" # SAP CLoud Platform Néo
CLOUD_FDY = "SCF" # SAP Cloud Platform Cloud Foundry
CLOUD_AWS = "AWS" # Amazon Web Services
CLOUD_AZR = "AZR" # Microsoft Azure
CLOUD_GCP = "GCP" # Google Cloud Platform
CLOUD_IBM = "IBM" # IBM Watson

"""DHT11 SENSOR CONFIG"""
DHT11_INSTRUCTION   = "DHT11"
CLOUD_REQUEST       = ""
RECEIVE_DHT11_INFOS = 0
MEASURES            = [0, 0]

# PARSING FUNCTIONS
def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))

def parse_scp_message(payload, search):
   """ Parse SCP Instruction message """
   subString = payload[payload.find(search):]
   isInstructionOnly = subString.find(",")
   if isInstructionOnly != -1:
       return(subString[len(search) + 3:subString.find(",") -1])
   else:
       return(subString[len(search) + 3:subString.find("}]}") -1])

# PUBLICATION FUNCTIONS
def publish_DHT11_measures(measures):
   """ Publish the measures to the cloud """
   for x in clients:
      client = x[0]
      if client.client_type == CLOUD_REQUEST == CLOUD_SCP:
         message =  '{"mode":"async", "messageType":"' + client.pushing_message_type + '","messages":[{'
         message += '"temperature":' + str(measures[0])
         message += ', "humidity":' + str(measures[1])
         message += ', "timestamp":' + str(int(time.time()))
         message += '}]}'
         client.publish(client.pub_topic, message)
      elif client.client_type == CLOUD_REQUEST == CLOUD_AWS:
         message = '{"temperature":' + str(measures[0])
         message += ', "humidity":' + str(measures[1])
         message += ', "timestamp":' + str(int(time.time()))
         message += '}'
         client.publish(client.pub_topic, message, 0)

def publish_message_to(client_id, message_to_publish):
    """ publish message to Client topic """
    for x in clients:
      client = x[0]
      if client.client_type != CLOUD_AWS:
         if client._client_id == client_id:
            client.publish(client.pub_topic, message_to_publish)

def publish_instruction(instruction):
   """ general method to publish instruction on the good Gateway topic """
   if instruction == DHT11_INSTRUCTION:
      publish_message_to("raspberry_broker", "0")
      publish_message_to("raspberry_broker", "1")

def on_publish(mqttc, obj, message_id):
   """ on_publish PAHO function """
   print("on_publish   - message_id: " + str(message_id))

# SUBSCRIBTION FUNCTIONS
def on_subscribe(client, obj, message_id, granted_qos):
    """ on_subscribe PAHO function """
    print("on_subscribe - message_id: " + str(message_id) + " / qos: " + str(granted_qos))

def format_subscription(topics):
   """ Format subscribtion to retreive topics """
   formated = []
   if len(topics) <= 1: return topics[0]
   for i in range(len(topics)):
      formated.append((topics[i], i))
   return formated

# CONNECTION FUNCTIONS
def on_connect(client, obj, flags, rc):
    """ on_connect PAHO function """
    print("on_connect   - rc: " + error_str(rc))
    client.connected_flag = True

def cleanup():
   """ Disconnect Client """
   for x in clients:
      client = x[0]
      if client.connected_flag:
         client.disconnect()

def on_disconnect(client, userdata, rc):
    """ on_disconnect PAHO function """
    print("disconnecting reason  " + error_str(rc))
    client.connected_flag = False

# MESSAGE FUNCTIONS
def on_message_broker(payload, init_topic, topics):
   """ wait for message on the broker, and assamble measures message """
   global RECEIVE_DHT11_INFOS
   global MEASURES
   if RECEIVE_DHT11_INFOS == 0:
      MEASURES = [0, 0]
   for i in range(len(topics)):
      if init_topic == topics[i]:
         if init_topic == topics[0]:
            MEASURES[0] = payload
            RECEIVE_DHT11_INFOS += 1
         elif init_topic == topics[1]:
            MEASURES[1] = payload
            RECEIVE_DHT11_INFOS += 1
         if RECEIVE_DHT11_INFOS == 2:
            publish_DHT11_measures(MEASURES)
            RECEIVE_DHT11_INFOS = 0

def on_message_aws(client, userdata, message):
   """ on_message special for AWS """
   payload = str(message.payload.decode("utf-8"))
   print("(AWS-message) " + str(message.topic) + " --> " + payload)
   subString = payload[payload.find("instruction"):]
   instruction = subString[len("instruction") + 4:subString.find("}") -2]
   global CLOUD_REQUEST
   CLOUD_REQUEST = CLOUD_AWS
   publish_instruction(instruction)

def on_message(client, userdata, message):
   """ PAHO on_message function """
   payload = str(message.payload.decode("utf-8"))
   print(payload)
   if client.client_type == CLOUD_SCP:
      print("(SCP-message) " + str(message.topic) + " --> " + payload)
      global CLOUD_REQUEST
      CLOUD_REQUEST = CLOUD_SCP
      if parse_scp_message(payload, "messageType") == client.instruction_message_type:
         publish_instruction(parse_scp_message(payload, "instruction"))
   if client._client_id == "raspberry_broker":
      print("(BROKER-message) " + str(message.topic) + " --> " + payload)
      on_message_broker(payload, message.topic, client.raw_sub_topic)

# MULTI-CLIENTS THREADING RELATIVE FUNCTIONS
def create_jwt(project_id, private_key_file, algorithm):
   """ Creates a JWT (https://jwt.io) to establish an MQTT connection.
       Return An MQTT generated from the given project_id and private key, which expires in 20 minutes.
       After 20 minutes, your client will be disconnected, and a new JWT will have to be generated. """
   token = {
       'iat': datetime.datetime.utcnow(), # The time that the token was issued at
       'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60), # The time the token expires.
       'aud': project_id # The audience field should always be set to the GCP project id.
   }
   with open(private_key_file, 'r') as f:
      private_key = f.read()
   print('Creating JWT using {} from private key file {}'.format(algorithm, private_key_file))
   return jwt.encode(token, private_key, algorithm=algorithm)

def create_clients():
   """ Create the clients for the broker_list """
   for i in range(len(broker.list)):

      if broker.list[i]["client_type"] == CLOUD_GCP:
         client = mqtt.Client(client_id=broker.list[i]["client_name"])
         client.username_pw_set(username='unused', password=create_jwt(broker.list[i]["client_name"], broker.list[i]["private_key_file"], broker.list[i]["algorithm"]))
         #client.tls_set(ca_certs=broker.list[i]["certificate"], tls_version=ssl.PROTOCOL_TLSv1_2)
      elif broker.list[i]["client_type"] == CLOUD_AWS:
         client = AWSIoTMQTTClient(broker.list[i]["client_name"], useWebsocket=True)
         client.configureEndpoint(broker.list[i]["broker_name"], broker.list[i]["port"])
         client.configureCredentials(broker.list[i]["certificate"])
      else:
         client = mqtt.Client(client_id=broker.list[i]["client_name"], transport=broker.list[i]["transport"])
         if broker.list[i]["client_type"] == CLOUD_SCP:
            client.ws_set_options(broker.list[i]["endpoint_path"])
            client.instruction_message_type = broker.list[i]["instruction_message_type"]
            client.pushing_message_type = broker.list[i]["pushing_message_type"]
         if broker.list[i]["username"] != "":
            client.username_pw_set(broker.list[i]["username"], broker.list[i]["password"])
         if broker.list[i]["certificate"] != "":
            client.tls_set(broker.list[i]["certificate"])
         client.on_connect = on_connect
         client.on_message = on_message
         client.on_disconnect = on_disconnect
         client.on_subscribe = on_subscribe
         client.on_publish = on_publish
      client.broker_name = broker.list[i]["broker_name"]
      client.port_number = broker.list[i]["port"]
      client.client_type = broker.list[i]["client_type"]
      client.pub_topic = broker.list[i]["pub_topic"]
      client.raw_sub_topic = broker.list[i]["sub_topic"]
      client.sub_topic = format_subscription(broker.list[i]["sub_topic"])
      client.connected_flag = False
      client.running_loop = True
      if client.client_type == CLOUD_IBM:
         print client.__dict__
      clients.append([client, False])

def multi_loop():
   """ Create the loop for each clients """
   while M_loop_flag:
      for x in clients:
         client = x[0]
         if client.client_type == CLOUD_AWS: None # while M_loop_flag: time.sleep(10)
         else: client.loop(.01)

def connect_and_subscribe(client, keep_alive):
   """ Connect the client and subscribe to the subscribtion topic for each """
   try:
      if client.client_type == CLOUD_AWS:
         res = client.connect()
         client.connected_flag = True
      else:
         res = client.connect(client.broker_name, client.port_number)
   except:
      print("Connexion Failed to " + str(broker_name))

   try:
      if client.client_type == CLOUD_AWS:
         r = client.subscribe(client.sub_topic, 1, on_message_aws)
      else:
         r = client.subscribe(client.sub_topic, qos=0)
   except Exception as e:
      print("Error to subscribe: " + str(e))

def connect_brokers():
   """ send the connection request in a thread """
   for x in clients:
      client = x[0]
      if not client.connected_flag:
         x[1] = False
         f = ex.submit(connect_and_subscribe, client, 60)
      else:
         x[1] = True

""" MAIN PROGRAM """
clients = []
nworkers = len(broker.list)
ex = futures.ThreadPoolExecutor(max_workers=(nworkers + 2))
create_clients()
M_loop_flag = True
t = threading.Thread(target=multi_loop)
t.start()
connect_brokers()

time.sleep(10)
M_loop_flag = False
cleanup()
