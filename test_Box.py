import requests

BASE_URL = "https://smartbox-chi.vercel.app/"
BOX_ID = 1 

def send_command_to_box(command_name):
    try:
        url = f"{BASE_URL}/api/send_command"
        payload = {
            "command": command_name,
            "box_id": BOX_ID
        }
        response = requests.post(url, json=payload)

        if response.status_code == 201:
            print(f"✅ Command '{command_name}' sent successfully to Box {BOX_ID}")
        else:
            print(f"❌ Failed to send command. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"⚠️ Error sending command: {e}")

def main():
    while True:
        print("\n=== Control Box via Supabase (Flask API on Vercel) ===")
        print("1. Send 'buzzer' command")
        print("2. Send 'led' command")
        print("3. Send 'servo' command")
        print("4. Send 'temp' command")
        print("q. Quit")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            send_command_to_box("buzzer")
        elif choice == '2':
            send_command_to_box("led")
        elif choice == '3':
            send_command_to_box("servo")
        elif choice == '4':
            send_command_to_box("temp")
        elif choice.lower() == 'q':
            print("👋 Exiting control interface.")
            break
        else:
            print("❌ Invalid input. Please enter 1-4 or q.")

if __name__ == '__main__':
    main()
