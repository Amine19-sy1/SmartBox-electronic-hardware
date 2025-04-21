    
from gpiozero import LED
from time import sleep

led = LED(17)  # Using GPIO17 (Pin 11)

# Step 1: Blink once
led.on()
print("LED ON (blink)")
sleep(1)

led.off()
print("LED OFF (blink)")
sleep(1)

# Step 2: Stay ON for 10 seconds
led.on()
print("LED ON for 10 seconds")
sleep(10)

# Step 3: Turn OFF at the end
led.off()
print("LED OFF")


