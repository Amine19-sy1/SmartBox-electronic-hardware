# Desktop/BuzzerStop.py
import RPi.GPIO as GPIO

BUZZER_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.LOW)
GPIO.cleanup()

print("Buzzer stopped and GPIO cleaned.")
