#!/usr/bin/python
# -*- coding: latin-1 -*-

import time, sys, threading, datetime, ssl
import paho.mqtt.client as mqtt
from concurrent import futures

try: from libs import broker_list as broker
except ImportError: print("Please fill the broker_list.py and configure appropriately !"); exit();
try: from libs import mqtt_functions as fnc
except ImportError: print("Please make sure to import the MQTT functions lib!"); exit();
try: from libs import sensors
except ImportError: print("The sensors.py file is missing!"); exit();
try: from config import config
except ImportError: print("Please fill the config.py and configure appropriately !"); exit();

CL            = broker.CL
CLOUD_REQUEST = ""
RECEIPT       = 0

# PUBLICATION FUNCTIONS
def format_cloud_message(client_type, sensor_type, measures):
   if client_type == CL["CLOUD_SCP"]:
      return '{"mode":"async", "messageType":"' + client.pushing_message_type + '","messages":[' + sensors.format_measures(sensor_type, measures) + ']}'
   else:
      return sensors.format_measures(sensor_type, measures)

def publish_cloud_message(sensor_type, measures):
   """ Publish the measures to the cloud """
   for x in clients:
      client = x[0]
      message = format_cloud_message(client.client_type, sensor_type, measures)
      if client.client_type == CLOUD_REQUEST == CL["CLOUD_SCP"]:
         client.publish(client.pub_topic, message)
      elif client.client_type == CLOUD_REQUEST == CL["CLOUD_AWS"]:
         client.publish(client.pub_topic, message, 0)

def publish_instruction(instruction):
   """ general method to publish instruction on the good Gateway topic """
   for x in clients:
      client = x[0]
      if client.client_type == "gateway":
         for i in range(len(config.SENSORS)):
            if instruction == config.SENSORS[i]["instruction"]:
               for j in range(len(config.SENSORS[i]["data"])):
                  client.publish(client.pub_topic, str(j))

# MESSAGE FUNCTIONS
def on_message_broker(payload, init_topic, topics):
   """ wait for message on the broker, and assamble measures message """
   sensor_type = init_topic[:init_topic.find("/")]
   selected_topics = []
   measures = []
   global RECEIPT

   for i in range(len(config.SENSORS)):
       if sensor_type == config.SENSORS[i]["name"]:
          for j in range(len(config.SENSORS[i]["pub_topics"])):
             selected_topics.append(config.SENSORS[i]["name"] + "/" + config.SENSORS[i]["pub_topics"][j])
          measures = config.SENSORS[i]["data"]

   if RECEIPT == 0: measures = config.SENSORS[i]["data"]

   for i in range(len(selected_topics)):
      if init_topic == selected_topics[i]:
         measures[i] = payload
         RECEIPT += 1
         if RECEIPT == len(selected_topics):
            publish_cloud_message(sensor_type, measures)
            RECEIPT = 0

def on_message(client, userdata, message):
   """ PAHO on_message function """
   payload = str(message.payload.decode("utf-8"))
   global CLOUD_REQUEST

   if client.client_type == CL["CLOUD_AWS"]:
      print("--> (AWS-message) " + str(message.topic) + " --> " + payload)
      subString = payload[payload.find("instruction"):]
      instruction = subString[len("instruction") + 4:subString.find("}") -2]
      CLOUD_REQUEST = CL["CLOUD_AWS"]
      publish_instruction(instruction)

   if client.client_type == CL["CLOUD_SCP"]:
      print("--> (SCP-message) " + str(message.topic) + " --> " + payload)
      CLOUD_REQUEST = CL["CLOUD_SCP"]
      if fnc.parse_scp_message(payload, "messageType") == client.instruction_message_type:
         publish_instruction(parse_scp_message(payload, "instruction"))

   if client.client_type == "gateway":
      print("--> (BROKER-message) " + str(message.topic) + " --> " + payload)
      on_message_broker(payload, message.topic, client.raw_sub_topic)

# MULTI-CLIENTS THREADING RELATIVE FUNCTIONS
def create_clients():
   """ Create the clients for the broker_list """
   for i in range(len(broker.list)):
      #if broker.list[i]["client_type"] == CL["CLOUD_GCP"]:
      #   client = mqtt.Client(client_id=broker.list[i]["client_name"])
      #   client.username_pw_set(username='unused', password=create_jwt(broker.list[i]["client_name"], broker.list[i]["private_key_file"], broker.list[i]["algorithm"]))
      #   client.tls_set(ca_certs=broker.list[i]["certificate"], tls_version=ssl.PROTOCOL_TLSv1_2)
      #if broker.list[i]["client_type"] == CL["CLOUD_SCP"]:
      #   client.ws_set_options(broker.list[i]["endpoint_path"])
      #   client.instruction_message_type = broker.list[i]["instruction_message_type"]
      #   client.pushing_message_type = broker.list[i]["pushing_message_type"]
      #   client.tls_set(broker.list[i]["certificate"])
      client = mqtt.Client(client_id=broker.list[i]["client_name"])
      if broker.list[i]["ssl"] == True:
         client.tls_set(
            broker.list[i]["certificate"],
            certfile=broker.list[i]["device_cert"],
            keyfile=broker.list[i]["key_path"],
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
            ciphers=None)
      if broker.list[i]["username"] != "":
         client.username_pw_set(broker.list[i]["username"], broker.list[i]["password"])
      client.on_connect = fnc.on_connect
      client.on_message = on_message
      client.on_disconnect = fnc.on_disconnect
      client.on_subscribe = fnc.on_subscribe
      client.on_publish = fnc.on_publish
      client.broker_name = broker.list[i]["broker_name"]
      client.port_number = broker.list[i]["port"]
      client.client_type = broker.list[i]["client_type"]
      client.pub_topic = broker.list[i]["pub_topic"]
      client.raw_sub_topic = broker.list[i]["sub_topic"]
      client.sub_topic = fnc.format_subscription(broker.list[i]["sub_topic"])
      client.connected_flag = False
      client.running_loop = True
      clients.append([client, False])

def multi_loop():
   """ Create the loop for each clients """
   while M_loop_flag:
      for x in clients:
         client = x[0]
         client.loop(.01)

def connect_and_subscribe(client, keep_alive):
   """ Connect the client and subscribe to the subscribtion topic for each """
   try: client.connect(client.broker_name, client.port_number, keep_alive)
   except: print("Connexion Failed to " + str(client.broker_name))
   try: client.subscribe(client.sub_topic, qos=0)
   except Exception as e: print("Error to subscribe: " + str(e))

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

#time.sleep(20)
#M_loop_flag = False
#fnc.cleanup(clients)
