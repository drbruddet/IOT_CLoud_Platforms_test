#include <ESP8266WiFi.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <PubSubClient.h>

const int D_ZERO = 16;
const int D_ONE = 5;
const int D_TWO = 4;
const int D_THREE = 0;
const int D_FOUR = 2;
const int D_FIVE = 14;
const int D_SIX = 12;
const int D_SEVEN = 13;
const int D_EIGHT = 15;

const char* ssid = "Wifi_SSID";
const char* password = "WifiPass";

const char* mqtt_server = "Raspberry IP";
const int   mqtt_server_port = 1883; // You can use normal 1884 port
const char* mqtt_user = "mosquitto_user";
const char* mqtt_password = "mosquitto_password";

const char* temperature_topic = "DHT11/temperature";
const char* humidity_topic = "DHT11/humidity";
const char* in_topic = "IN/instruction";

const char  temperature_instruction = '0';
const char  humidity_instruction = '1';

long  lastMsg = 0;
float temp    = 0.0;
float hum     = 0.0;
float diff    = 1.0;

WiFiClient espClient;
PubSubClient client(espClient);

#define DHTPIN D_ONE
#define DHTTYPE DHT11
DHT_Unified dht(DHTPIN, DHTTYPE);

/*
 * WIFI FUNCTIONS
*/

bool setupWifi() {
  Serial.println();
  WiFi.begin(ssid, password);
  Serial.print("Connecting");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected, IP address: ");
  Serial.println(WiFi.localIP());
  return WiFi.localIP() ? true : false;
}

/*
 * LIGHTS FUNCTIONS
*/

void connectWifiLight() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(200);
  digitalWrite(LED_BUILTIN, LOW);
  delay(5000);
}

void brightContinueSensorLight() {
  digitalWrite(D_TWO, HIGH);
}

void brightContinueMQTTLight() {
  digitalWrite(D_SIX, HIGH);
}

void brightFlashTemperatureLightOn() {
  digitalWrite(D_FOUR, HIGH);
}

void brightFlashTemperatureLightOff() {
  digitalWrite(D_FOUR, LOW);
}

void brightFlashHumidityLightOn() {
  digitalWrite(D_FIVE, HIGH);
}

void brightFlashHumidityLightOff() {
  digitalWrite(D_FIVE, LOW);
}

/*
 * SENSORS FUNCTIONS
*/

bool setupSensor() {
  dht.begin();
  Serial.println();
  Serial.println("Temperature and Humidity Sensor Status");
  sensor_t sensor;
  dht.temperature().getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.println("Temperature");
  Serial.print  ("Sensor:       "); Serial.println(sensor.name);
  Serial.print  ("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print  ("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print  ("Max Value:    "); Serial.print(sensor.max_value); Serial.println(" *C");
  Serial.print  ("Min Value:    "); Serial.print(sensor.min_value); Serial.println(" *C");
  Serial.print  ("Resolution:   "); Serial.print(sensor.resolution); Serial.println(" *C");  
  Serial.println("------------------------------------");
  dht.humidity().getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.println("Humidity");
  Serial.print  ("Sensor:       "); Serial.println(sensor.name);
  Serial.print  ("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print  ("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print  ("Max Value:    "); Serial.print(sensor.max_value); Serial.println("%");
  Serial.print  ("Min Value:    "); Serial.print(sensor.min_value); Serial.println("%");
  Serial.print  ("Resolution:   "); Serial.print(sensor.resolution); Serial.println("%");  
  Serial.println("------------------------------------");
  return true;
}

/*
 * MQTT FUNCTIONS
*/

void publishTemperatureData() {
  sensors_event_t event;
  dht.temperature().getEvent(&event);
  float newTemp = event.temperature;
  brightFlashTemperatureLightOn();
  temp = newTemp;
  Serial.print("Temperature: ");
  Serial.print(String(temp).c_str());
  Serial.println(" *C");
  if (client.connected()) {
     client.publish(temperature_topic, String(temp).c_str(), true);
     Serial.println(" Published Temperature message");
   } else {
     Serial.println("Temperature Publication failed");
   }
   delay(1000);
   brightFlashTemperatureLightOff();
}

void publishHumidityData() {
  sensors_event_t event;
  dht.humidity().getEvent(&event);
  float newHum = event.relative_humidity;
  brightFlashHumidityLightOn();
  hum = newHum;
  Serial.print("Humidity: ");
  Serial.print(String(hum).c_str());
  Serial.println("%");
  if (client.connected()) {
    client.publish(humidity_topic, String(hum).c_str(), true);
    Serial.println(" Published Humidity message");
  } else {
     Serial.println("Humidity Publication failed");
  }
  delay(1000);
  brightFlashHumidityLightOff();
}

void onMQTTMessage(char* topic, byte* payload, unsigned int length) {
  Serial.println("-----------------------");
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
  Serial.println("-----------------------");

  if ((char)payload[0] == temperature_instruction) {
    publishTemperatureData();
  } else if ((char)payload[0] == humidity_instruction) {
    publishHumidityData();
  } else {
    Serial.print("The instruction is not understood! Can't process...");
  }
}

void setupMQTTClient() {
  client.setServer(mqtt_server, mqtt_server_port);
  client.setCallback(onMQTTMessage);

  while (!client.connected()) {
    Serial.println("Connecting to MQTT...");
    if (client.connect("ESP8266-1", mqtt_user, mqtt_password)) {
      Serial.println("connected");
      brightContinueMQTTLight();
      client.subscribe(in_topic);
    } else {
      Serial.print("failed with state ");
      Serial.print(client.state());
      delay(2000);
    }
  }
}

/*
 * PROGRAM SETUP
*/
void setup() {
  Serial.begin(9600);
  if (setupSensor()) {
    pinMode(D_TWO, OUTPUT);
    pinMode(D_FOUR, OUTPUT);
    pinMode(D_FIVE, OUTPUT);
    pinMode(D_SIX, OUTPUT);
    brightContinueSensorLight();
  }
  if (setupWifi()) {
    pinMode(LED_BUILTIN, OUTPUT);
    connectWifiLight();
  }
  setupMQTTClient();
}

/*
 * PROGRAM LOOP
*/

void loop() {
  client.loop();
}
