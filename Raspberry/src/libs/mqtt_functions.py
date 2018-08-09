import sys, ssl
import paho.mqtt.client as mqtt

def error_str(rc):
   """Convert a Paho error to a human readable string."""
   return '{}: {}'.format(rc, mqtt.error_string(rc))

def on_publish(mqttc, obj, message_id):
   """ on_publish PAHO function """
   print("on_publish   - message_id: " + str(message_id))

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

def on_connect(client, obj, flags, rc):
   """ on_connect PAHO function """
   print("on_connect   - rc: " + error_str(rc))
   client.connected_flag = True

def cleanup(clients):
   """ Disconnect Client """
   for x in clients:
      client = x[0]
      if client.connected_flag:
         client.disconnect()

def on_disconnect(client, userdata, rc):
   """ on_disconnect PAHO function """
   print("disconnecting reason  " + error_str(rc))
   client.connected_flag = False

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

# CLOUDS FIUNCTIONS
def parse_scp_message(payload, search):
   """ Parse SCP Instruction message """
   subString = payload[payload.find(search):]
   isInstructionOnly = subString.find(",")
   if isInstructionOnly != -1:
       return(subString[len(search) + 3:subString.find(",") -1])
   else:
       return(subString[len(search) + 3:subString.find("}]}") -1])

