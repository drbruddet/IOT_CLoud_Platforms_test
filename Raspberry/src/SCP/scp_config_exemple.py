# SCP ACCOUNT CONFIG
scp_account_id='s---------trial'
scp_landscape_host='.hanatrial.ondemand.com'

# DEVICE CONFIG
endpoint_certificate = "SCP/hanatrial.ondemand.com.crt"
device_id="--------------------"
oauth_credentials_for_device="------------------"

# TOPICS

""" Cloud Message Type (cloud to device): 
    -> instruction (String) """
in_topic = "-------------------"


""" Device Message Type (device to cloud):
    -> timestamp (date)
    -> temperature (float)
    -> humidity (float)
"""
out_topic = "-------------------"
