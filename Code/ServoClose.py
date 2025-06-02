import RPi.GPIO as GPIO
import time

SERVO_PIN = 22

def set_angle(angle):
    duty = 2.5 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

try:
    print("Fermeture servo (0°)")
    set_angle(0)

finally:
    pwm.stop()
    GPIO.cleanup()
    print("Servo fermé et GPIO nettoyé.")
