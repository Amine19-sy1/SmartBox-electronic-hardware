import RPi.GPIO as GPIO
import dht11
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
instance = dht11.DHT11(pin=23)

print("Testing DHT11 on GPIO 23...")

for i in range(0, 20):
    result = instance.read()
    if result.is_valid():
        print(f"Temperature: {result.temperature}°C, Humidity: {result.humidity}%")
    else:
        print("Read failed")
    time.sleep(1)



