# IOT_CLoud_Platforms_test
Testing different IoT platform with the MQTT Protocol.
* SAP Cloud Platform IoT (Néo)
* Amazon Web Services

The configuration contain a Raspberry acting as a gateway and an Arduino ESP8266 with a DHT11 (humidity & temperature sensor) acting as sensor platform. The clouds has to send an instruction message where the Gateway recieve it and treat it with is own MQTT Broker.
Then, instructions are sent to the Arduino who send back the sensors data to the cloud though the Gateway. The gateway's goal is to assemble the messages but it can also proceed to some edge processing.

## 1. install your mosquitto broker on the Raspberry PI

### A. Install Mosquitto Broker on Raspberry PI:

In your raspberry terminal:
```
$> wget http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key
$> sudo apt-key add mosquitto-repo.gpg.key
$> cd /etc/apt/sources.list.d/
CHOICE ONE: for wheezy $> sudo wget http://repo.mosquitto.org/debian/mosquitto-wheezy.list
CHOICE TWO: for jessie $> sudo wget http://repo.mosquitto.org/debian/mosquitto-wheezy.list
$> sudo apt-get update
$> sudo apt-get install mosquitto
$> sudo systemctl enable mosquitto.service

Test the installation with: $> mosquitto -v
```
> Note: sometimes the command mosquitto -v prompts a warning message saying “1484326030:
> Error: Address already in use”.
> That warning message means that your Mosquitto Broker is already running, so don’t worry about that.

### B. Install Mosquitto Client on Raspberry PI:

``` $> sudo apt-get install mosquitto-clients ```

### C. Test the broker

* In Terminal 1:
``` $> mosquitto_sub –d –t test_mqtt ```

* In Terminal 2:
``` $> mosquitto_pub –d –t test_mqtt –m “Hello World” ```

Then, you should see the "Hello World" on the termnial 1.

To test from another computer (Imagine your raspberry IP is: 192.168.1.10), then:

``` $> mosquitto_pub -h 192.168.1.10 -t test_mqtt -m "Hi this is Me" ```

### D. Configure and secure your broker

Configure your mosquitto config /etc/mosquitto/mosquitto.conf
```
allow_anonymous false
password_file /etc/mosquitto/pwfile
```

then, you will need a /etc/mosquitto/pwfile file.

* To generate a password file, I recommand to do: (change your_user and your_password) (use sudo if needed)

```
$> echo "your_user:your_password" > /etc/mosquitto/pwfile
$> mosquitto_passwd -U /etc/mosquitto/pwfile
```

Or if you don't want to authentify:
``` allow_anonymous true ```

> You can find in this project my mosquitto.conf file in the Raspberry/config directory.

Then, restart mosquitto:
```$> sudo systemctl restart mosquitto ```

## 2. Setup your Arduino

### A. Change few settings in code Arduino/program.cpp:
```
const char* ssid = "your wifi SSID";
const char* password = "your Wifi Password";

const char* mqtt_server = "your Raspberry IP address";
const int   mqtt_server_port = 1883; // you can set the normal 1884 port

// If your raspberry mosquitto broker config you set the allow_anonymous false and the user / password
const char* mqtt_user = "mosquitto_user";
const char* mqtt_password = "mosquitto_pass";

// Set the different topics you will use
const char* temperature_topic = "DHT11/temperature";
const char* humidity_topic = "DHT11/humidity";
const char* in_topic = "IN/instruction";
```

### B. Connect the Arduino / sensor / lights:

I'm using pins:
- D1: Data pin from sensor
- D2: the brightContinueLight meaning the sensor is working
- D4: the brightFlashLightOn/off meaning the data TEMPERATURE is sending
- D5: the brightFlashLightOn/off meaning the data HUMIDITY is sending
- D6: the brightContinueLight meaning the MQTT client is connected

![Pin Sensor](https://preview.ibb.co/dpROg8/Node_MCU_DHT11_Interfacing.png)
![Pin Sensor with LED](https://preview.ibb.co/kM7Nto/IMG_9437.jpg)

**_For Arduino, when you flash a new version of your program, don't forget to push the arduino flash button first._**

### C. You should retreive data in the Arduino Serial Monitor
_Don't forget to set in the monitor 9600 Baud setting as my code, or change it in the code._

![SCREENSHOT Data](https://preview.ibb.co/i3PLTo/Capture_d_e_cran_2018_07_25_a_11_19_27.jpg)

### D. Connect Raspberry Gateway to the good topics

Open three termnial on your raspberry, and in each: (adapt if you set user / password or not)
```
$1 > if ($> systemctl status mosquitto show you that is not already active) --> then: $> mosquitto
$2 > mosquitto_sub -d -u (user) -P (password) -t (TOPIC_temperature)
$3 > mosquitto_sub -d -u (user) -P (password) -t (TOPIC_humidity)
```

### E. Test the service to ask sensors data from devices:

Once you subscribes in the Rasberry terminal to the two output topics, you can send a publication on the input topic:

In my prgoram code (you can change it):
```
const char  temperature_instruction = '0';
const char  humidity_instruction = '1';
```

* From your raspberry (adapt your port and if you set a login/pass):
```
$> mosquitto_pub -h 127.0.0.1 -p 1883 -t IN/instruction -m "0"
$> mosquitto_pub -h 127.0.0.1 -p 1883 -t IN/instruction -m "1" -u LOGIN -P PASSWORD
```

* From another device (adapt your port and if you set a login/pass, but also your IP address):
```
$> mosquitto_pub -h 192.168.1.10 -p 1883 -t IN/instruction -m "0"
$> mosquitto_pub -h 127.0.0.1 -p 1883 -t IN/instruction -m "1" -u LOGIN -P PASSWORD
```

## 3. Cloud part

### A. Setup your cloud environnement

I will pass on the different cloud configs, but here are some tutos:

* SAP Cloud Platform (Néo)

[HCP Service IOT](https://www.sap.com/developer/tutorials/iot-part6-hcp-services.html)
[IoT StarterKit](https://github.com/SAP/iot-starterkit/tree/master/neo)

* Amazon Web Services

[With AWS Command Line Interface](https://docs.aws.amazon.com/cli/latest/userguide/installing.html)

> Of course, do your own researches to be sure to set your own working configuration.

### B. Change your cloud config file

> You will have to do it for each cloud services you want to activate.

* Change your (cloud)_config_exemple.py to (cloud)_config.py
* if you need some certificates or tokens, make sure to download it from your cloud provider. It's thing related, you should be able to download easily in the related Cloud directory ex: AWS/ or SCP/
* Open the file and set the requested configs

## 4. Launch the apps

You can now test everything launching the mqtt_app.py file on your raspberry. (every files in the RASPBERRY folder should be  downloaded on the Raspberry)
```
$> python mqtt_app.py
```
> Don't forget to launch your mosquitto broker on the raspberry.

ENJOY!
