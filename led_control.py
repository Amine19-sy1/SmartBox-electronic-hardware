from gpiozero import LED, Buzzer
from time import sleep

# Define LED and Buzzer
led = LED(17)  # LED connected to GPIO17
buzzer = Buzzer(18)  # Buzzer connected to GPIO18

while True:
    led.on()
    buzzer.on()
    print("LED and Buzzer ON")
    sleep(1)

    led.off()
    buzzer.off()
    print("LED and Buzzer OFF")
    sleep(1)
