import RPi.GPIO as GPIO
import time

# Set GPIO pin
BUZZER_PIN = 17  # Change if using a different GPIO

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Start PWM with 1kHz frequency
pwm = GPIO.PWM(BUZZER_PIN, 1000)
pwm.start(0)  # Start with 0% duty cycle (silent)

try:
    for i in range(2):  # Play the tone two times
        print(f"Playing tone {i+1}...")
        pwm.ChangeFrequency(1000)  # 1000 Hz tone
        pwm.ChangeDutyCycle(50)    # 50% duty cycle (sound on)
        time.sleep(5)              # Play for 5 seconds
        pwm.ChangeDutyCycle(0)     # Stop
        print("Stopping tone...")
        time.sleep(1)              # 1 sec pause before repeating

    # Optional: Play a melody after that
    print("Playing melody...")
    notes = [262, 294, 330, 349, 392, 440, 494, 523]  # Do Re Mi...
    for note in notes:
        pwm.ChangeFrequency(note)
        pwm.ChangeDutyCycle(50)
        time.sleep(0.3)
        pwm.ChangeDutyCycle(0)
        time.sleep(0.05)

finally:
    pwm.stop()
    GPIO.cleanup()
    print("Buzzer stopped and GPIO cleaned up.")


