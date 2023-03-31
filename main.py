###Error codes
# 1 flash is connection established
# 2 flash is awaiting ip
# 3 flash is connection failure
# 4 flash is ssid not found
# 5 flash is bad auth
# 6 flash is sensor failure
# 10 flash is network return out of bounds



from machine import Pin
import dht
import time
import ubinascii
import network
from  umqtt_simple import MQTTClient

### Setup
#led setup
led = machine.Pin("LED", Pin.OUT, value=1)
led.off()



# MQTT Setup
BROKER = '***.***.***.***'
PORT = 1883
TOPIC = '***'
user = '***'
mpassword = '***'
client_id = str(time.time())
client = MQTTClient(client_id, BROKER, PORT, user, mpassword)

# Wifi init
network.country("AU")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
ap_list = wlan.scan()
ssid = '***'
password = '***'


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
            blink_led(0.2, 1)
            time.sleep(2)
        elif wlan.status() == 2:
            blink_led(0.2, 2)
            time.sleep(2)
        elif wlan.status() == 3:
            led.on()
            print('Connected')
            break
        elif wlan.status() == -1:
            blink_led(0.2, 3)
            time.sleep(2)
        elif wlan.status() == -2:
            blink_led(0.2, 4)
            time.sleep(2)
        elif wlan.status() == -3:
            blink_led(0.2, 5)
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
        blink_led(0.2, 6)
        time.sleep(2)
        led.on()
        return None, None

def reconnect():
    attempt = 0
    while True:
        try:
            client.connect()
            print('Successfully connected to the MQTT broker')
            break
        except OSError as e:
            attempt += 1
            print('Failed to connect to the MQTT broker (attempt {}): {}'.format(attempt, e))
            if attempt >= 5:
                print('Max connection attempts reached. Resetting the device...')
                time.sleep(5)
                machine.reset()
            time.sleep(5)




# Send average data to Broker
def send_payload():
    temperature1, humidity1 = read_dht22_data(dht_sensor1)
    temperature2, humidity2 = read_dht22_data(dht_sensor2)
    try:
        client.connect()
    except OSError as e:
        reconnect()
        
    
    if temperature1 is not None and humidity1 is not None and temperature2 is not None and humidity2 is not None:
        
        avg_temperature = (temperature1 + temperature2) / 2
        avg_humidity = (humidity1 + humidity2) / 2
        
        payload = "Average Temperature: {:.2f}C, Average Humidity: {:.2f}%".format(avg_temperature, avg_humidity)
        client.publish(TOPIC, payload)  # TOPIC should be defined with the desired topic string
        print(payload)
    else:
        print("Failed to read data from one or both sensors")
    client.disconnect()
    wlan.disconnect()
    led.off()
    
###main loop        
while True:
    conn_check()
    send_payload()
    print("done")
    time.sleep(30)  # Wait for 30 seconds before reading again
    



