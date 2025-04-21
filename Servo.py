
import RPi.GPIO as GPIO
import time

SERVO_PIN = 17  # Change this to your GPIO pin

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# PWM at 50Hz (20ms period)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

def set_angle(angle):
    duty = 2 + (angle / 18)  # Map 0-180° to 2-12% duty
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        user_input = input("Enter 1 to open (180°), 0 to close (0°), or q to quit: ")
        if user_input == '1':
            print("Opening (180 degrees)")
            set_angle(180)
        elif user_input == '0':
            print("Closing (0 degrees)")
            set_angle(0)
        elif user_input.lower() == 'q':
            print("Exiting program.")
            break
        else:
            print("Invalid input. Please enter 1, 0, or q.")

finally:
    pwm.stop()
    GPIO.cleanup()
    print("GPIO cleaned up.")


