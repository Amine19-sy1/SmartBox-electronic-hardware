#!/usr/bin/env python3

import subprocess
import bluetooth
import os
import time
import signal

BOXINFO_FILE = os.path.expanduser("Boxinfo.txt")
AGENT_PATH = "bluetooth_auto_agent.py"

def launch_bluetooth_agent():
    print("Starting Bluetooth pairing agent...")
    return subprocess.Popen(["python3", AGENT_PATH])

def save_wifi_info(ssid, password, user_id):
    print(f"Saving Wi-Fi info to Boxinfo.txt...")
    lines = []
    if os.path.exists(BOXINFO_FILE):
        with open(BOXINFO_FILE, "r") as f:
            # Lire les lignes sans lignes vides ni sauts multiples
            lines = [line.rstrip('\n') for line in f if line.strip()]

    new_lines = []
    found_ssid = found_password = found_user_id = False

    for line in lines:
        if line.startswith("SSID="):
            new_lines.append(f"SSID={ssid}")
            found_ssid = True
        elif line.startswith("PASSWORD="):
            new_lines.append(f"PASSWORD={password}")
            found_password = True
        elif line.startswith("USER_ID="):
            new_lines.append(f"USER_ID={user_id}")
            found_user_id = True
        else:
            new_lines.append(line)

    if not found_ssid:
        new_lines.append(f"SSID={ssid}")
    if not found_password:
        new_lines.append(f"PASSWORD={password}")
    if not found_user_id:
        inserted = False
        updated_lines = []
        for l in new_lines:
            updated_lines.append(l)
            if not inserted and l.startswith("BOX_ID="):
                updated_lines.append(f"USER_ID={user_id}")
                inserted = True
        new_lines = updated_lines

    with open(BOXINFO_FILE, "w") as f:
        # Écrit chaque ligne avec un seul saut de ligne
        f.write('\n'.join(new_lines) + '\n')

    print("Wi-Fi and User ID info saved.")

def add_wifi_network(ssid, password, user_id):
    print(f"Adding Wi-Fi config for SSID: {ssid}")
    subprocess.run(["nmcli", "connection", "delete", ssid], stderr=subprocess.DEVNULL)
    subprocess.run(["nmcli", "device", "wifi", "rescan"])
    time.sleep(2)
    save_wifi_info(ssid, password, user_id)

    result = subprocess.run([
        "nmcli", "device", "wifi", "connect", ssid,
        "password", password,
        "name", ssid
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("Wi-Fi credentials added and connected successfully.")
    else:
        print(f"Failed to connect: {result.stderr}")

def free_rfcomm_port():
    print("Checking and freeing RFCOMM port 1 if needed...")
    try:
        # Try to release all RFCOMM ports (safe even if none used)
        subprocess.run(["sudo", "rfcomm", "release", "all"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Kill known blockers (like previous bluetoothd or python scripts)
        subprocess.run(["sudo", "fuser", "-k", "/dev/rfcomm1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("RFCOMM port released successfully.")
    except Exception as e:
        print(f"Could not release RFCOMM port: {e}")

def start_rfcomm_server():
    free_rfcomm_port()
    try:
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_sock.bind(("", 1))
        server_sock.listen(1)
        print("Waiting for Bluetooth connection on channel 1...")
    except bluetooth.btcommon.BluetoothError as e:
        print(f"Failed to bind RFCOMM socket: {e}")
        print("Suggestion: Wait a few seconds and retry or reboot the device.")
        return

    while True:
        try:
            client_sock, client_info = server_sock.accept()
            print(f"Connected to {client_info}")
            data = client_sock.recv(1024).decode().strip()
            print(f"Received: {data}")

            if "," in data:
                parts = data.split(",", 2)
                if len(parts) == 3:
                    ssid, password, user_id = parts
                    add_wifi_network(ssid.strip(), password.strip(), user_id.strip())
                    client_sock.send("Wi-Fi credentials and user ID received and connected.\n".encode())
                else:
                    client_sock.send("Invalid format. Use: ssid,password,user_id\n".encode())
            else:
                client_sock.send("Invalid format. Use: ssid,password,user_id\n".encode())

            client_sock.close()
        except Exception as e:
            print(f"Error: {e}")
            break

    server_sock.close()

if __name__ == "__main__":
    agent_process = launch_bluetooth_agent()

    try:
        time.sleep(3)
        start_rfcomm_server()
    finally:
        print("Stopping Bluetooth agent...")
        agent_process.terminate()
