###Error codes
# 1 flash is connection established
# 2 flash is awaiting ip
# 3 flash is connection failure
# 4 flash is ssid not found
# 5 flash is bad auth
# 6 flash is sensor failure
# 10 flash is network return out of bounds



import machine
import dht
import time
import ubinascii
import network
import rp2
from umqtt_simple import MQTTClient

### Setup
#led setup
led = Pin("LED", Pin.OUT, value=1)
led.off()

# Wifi settings
ssid = 'Wireless Network'
password = 'The Password'

# MQTT Setup
BROKER = 'your_broker_hostname_or_ip'
PORT = 1883
TOPIC = 'sensor'
client_id = 'Pico-' + ubinascii.hexlify(machine.unique_id()).decode() # Generate a unique client ID for MQTT
client = MQTTClient(client_id, BROKER, PORT)

# Wifi init
rp2.country('AU')
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Configure the pins for the DHT22 sensors
dht_sensor1 = dht.DHT22(machine.Pin(3))
dht_sensor2 = dht.DHT22(machine.Pin(4))

#### functions        
#Handle net connection
def conn_check():
    while True:
        if wlan.status() == 0:
            wlan.connect(ssid, password)
        elif wlan.status() == 1:
            blink_led(0.5, 1)
            time.sleep(2)
        elif wlan.status() == 2:
            blink_led(0.5, 2)
            time.sleep(2)
        elif wlan.status() == 3:
            led.on()
            break
        elif wlan.status() == -1:
            blink_led(0.5, 3)
            wlan.connect(ssid, password)
            time.sleep(2)
        elif wlan.status() == -2:
            blink_led(0.5, 4)
            wlan.connect(ssid, password)
            time.sleep(2)
        elif wlan.status() == -3:
            blink_led(0.5, 5)
            wlan.connect(ssid, password)
            time.sleep(2)
        else:
            blink_led(0.1, 10)
            raise Exception("network loop error")

#Error blink code
def blink_led(frequency = 0.5, num_blinks = 1):
    for _ in range(num_blinks):
        led.off()
        time.sleep(frequency)
        led.on()
        time.sleep(frequency)
        led.off()
        time.sleep(frequency)

#read DHT22
def read_dht22_data(sensor):
    try:
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        return temperature, humidity
    except OSError:
        blink_led(0.5, 6)
        time.sleep(2)
        led.on
        return None, None

# Send average data to Broker
def send_payload():
    temperature1, humidity1 = read_dht22_data(dht_sensor1)
    temperature2, humidity2 = read_dht22_data(dht_sensor2)
    client.connect()#mqtt connect
    if temperature1 is not None and humidity1 is not None and temperature2 is not None and humidity2 is not None:
        
        avg_temperature = (temperature1 + temperature2) / 2
        avg_humidity = (humidity1 + humidity2) / 2
        
        payload = "Average Temperature: {:.2f}C, Average Humidity: {:.2f}%".format(avg_temperature, avg_humidity)
        client.publish(TOPIC, payload)  # TOPIC should be defined with the desired topic string
        print(payload)
    else:
        print("Failed to read data from one or both sensors")
    client.disconnect()
    
    
###main loop        
while True:
    if machine.Pin(7, machine.IN, machine.PULL_UP).value() == 1:
        break
    else:
        conn_check()
        send_payload()
    time.sleep(30)  # Wait for 30 seconds before reading again
    
