
import subprocess

def run_script(script_name):
    try:
        subprocess.run(['python3', f'{script_name}'])
    except Exception as e:
        print(f"Error running {script_name}: {e}")

def main():
    while True:
        print("\n=== Control Box Menu ===")
        print("1. Activate Buzzer")
        print("2. Blink LED then turn ON for 10s")
        print("3. Control Servo (manual input)")
        print("4. Log Temperature for 10 seconds")
        print("q. Quit")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            run_script('Buzzer.py')
        elif choice == '2':
            run_script('Led.py')
        elif choice == '3':
            run_script('Servo.py')
        elif choice == '4':
            run_script('TempLogger.py')
        elif choice.lower() == 'q':
            print("Exiting control box.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
