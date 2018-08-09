# CLIENT
client         = "client_name"
endpoint       = "NAME.iot.ZONE.amazonaws.com"

# PROTOCOL #https://docs.aws.amazon.com/fr_fr/iot/latest/developerguide/protocols.html
ssl            = True
port           = 8883
transport      = "tcp"
root_ca_path   = "config/cloud/AWS/aws-iot-rootCA.crt"
device_ca_path = "config/cloud/AWS/cert.pem"
key_path       = "config/cloud/AWS/privkey.pem"
public_key     = "config/cloud/AWS/publicKey.pem"

# TOPICS
sub_topic      = "AWS/instruction"
pub_topic      = "AWS/DHT11Data"
