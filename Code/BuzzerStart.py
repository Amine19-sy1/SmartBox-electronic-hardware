# Desktop/BuzzerStart.py
import RPi.GPIO as GPIO
import time
import signal
import sys
import subprocess
import os

BUZZER_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

pwm = GPIO.PWM(BUZZER_PIN, 1000)  # 1kHz
pwm.start(0)  # Start with 0% duty cycle (OFF)

def handle_exit(signum, frame):
    print("Stopping buzzer...")
    pwm.stop()
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

print(" Alternating buzzer for 5 seconds...")

start_time = time.time()
duration = 5  # seconds

try:
    while time.time() - start_time < duration:
        pwm.ChangeDutyCycle(80)  # ON
        time.sleep(0.2)
        pwm.ChangeDutyCycle(0)   # OFF
        time.sleep(0.2)
except KeyboardInterrupt:
    handle_exit(None, None)

print("Done buzzing. Calling BuzzerStop.py...")

pwm.stop()
GPIO.cleanup()

# Call BuzzerStop.py
try:
    subprocess.run(["python3", os.path.expanduser("~/Desktop/BuzzerStop.py")])
except Exception as e:
    print(f"Error calling BuzzerStop.py: {e}")
