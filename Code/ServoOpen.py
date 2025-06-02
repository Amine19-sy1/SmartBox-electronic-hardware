import RPi.GPIO as GPIO
import time

SERVO_PIN = 22  # Broche GPIO du signal

def set_angle(angle):
    # Ajusté pour MG996R : 2.5 + angle/18 pour une rotation plus fiable
    duty = 2.5 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)  # Stop pour éviter bruit/chauffe

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    pwm = GPIO.PWM(SERVO_PIN, 50)  # Fréquence PWM : 50 Hz
    pwm.start(0)

    print("Ouverture servo (180°)")
    set_angle(180)

except Exception as e:
    print(f"Erreur dans ServoOpen.py: {e}")

finally:
    pwm.stop()
    GPIO.cleanup()
    print("Servo ouvert et GPIO nettoyé.")
