import time

# DHT11 SENSOR FUNCTIONS
def DHT11_format_measures(measures):
   return '{"temperature":' + str(measures[0]) + ', "humidity":' + str(measures[1]) + ', "timestamp":' + str(int(time.time())) + '}'

def format_measures(measure_type, measures):
   if measure_type == "DHT11":
      return DHT11_format_measures(measures)
