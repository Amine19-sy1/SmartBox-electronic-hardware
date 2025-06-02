import time
import subprocess
import os
import signal
import socket
import threading
from dotenv import load_dotenv
from supabase import create_client

import gpiozero
from gpiozero.pins.rpigpio import RPiGPIOFactory
gpiozero.Device.pin_factory = RPiGPIOFactory()

from gpiozero import LED

# S'assurer que le périphérique HID est accessible
subprocess.run(["sudo", "chmod", "a+rw", "/dev/hidraw0"])

#  Chemins
BOXINFO_FILE = os.path.expanduser("~/Desktop/Boxinfo.txt")
WIFI_SERVER_PATH = os.path.expanduser("~/Desktop/wifi_rfcomm_server.py")
AUTHORIZED_FILE = os.path.expanduser("~/Desktop/authorized_ids.txt")
HID_PATH = "/dev/hidraw0"

#  LEDs
try:
    led_rouge = LED(27)  # GPIO 27 = LED rouge
    led_vert = LED(25)   # GPIO 25 = LED verte
    led_init_success = True
except Exception as e:
    print(f"Erreur initialisation GPIO: {e}")
    led_rouge = led_vert = None
    led_init_success = False

# Contrôle du clignotement
blinking = False
blink_thread = None

# État de la boîte (0: fermé, 1: ouvert)
box_open = False

def start_blinking_red_led():
    global blinking, blink_thread
    if not led_init_success: return
    blinking = True

    def blink():
        while blinking:
            led_rouge.on()
            time.sleep(0.5)
            led_rouge.off()
            time.sleep(0.5)

    blink_thread = threading.Thread(target=blink)
    blink_thread.start()

def stop_blinking_red_led():
    global blinking, blink_thread
    if not led_init_success: return
    blinking = False
    if blink_thread:
        blink_thread.join()
    led_rouge.on()

if led_init_success and led_rouge:
    led_rouge.on()
print("LED rouge allumée (listener actif)")

def start_bluetooth_adapter():
    print(" Activating Bluetooth adapter...")
    subprocess.run(["sudo", "hciconfig", "hci0", "up"], stderr=subprocess.DEVNULL)
    print("Bluetooth adapter is up.")

def is_wifi_connected():
    try:
        subprocess.check_output(["ping", "-c", "1", "-W", "1", "8.8.8.8"], stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def scan_and_connect_wifi():
    print("Scanning for available Wi-Fi networks...")
    try:
        result = subprocess.check_output(["nmcli", "-t", "-f", "SSID", "dev", "wifi"], stderr=subprocess.DEVNULL).decode()
        networks = list(set([ssid.strip() for ssid in result.split('\n') if ssid.strip()]))

        print(f"Found networks: {networks}")
        for ssid in networks:
            print(f"Trying to connect to {ssid}...")
            connect_result = subprocess.run(["nmcli", "device", "wifi", "connect", ssid], capture_output=True)
            time.sleep(3)
            if is_wifi_connected():
                print(f"Successfully connected to {ssid}")
                return True
            else:
                print(f"Failed to connect to {ssid}")
        return False
    except Exception as e:
        print(f"Error while scanning Wi-Fi: {e}")
        return False

def load_box_info():
    box_info = {}
    if os.path.exists(BOXINFO_FILE):
        with open(BOXINFO_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    value = value.split("#")[0].strip()
                    box_info[key.strip()] = value
    return box_info

def load_authorized_ids():
    try:
        with open(AUTHORIZED_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    except Exception as e:
        print(f"Erreur chargement fichier: {e}")
        return set()

class BluetoothManager:
    def __init__(self):
        self.process = None

    def start(self):
        if self.process is None or self.process.poll() is not None:
            print("Starting Bluetooth receiver server...")
            self.process = subprocess.Popen(["sudo", "python3", WIFI_SERVER_PATH])
            print("Bluetooth receiver started.")

    def stop(self):
        if self.process and self.process.poll() is None:
            print("Stopping Bluetooth receiver server...")
            self.process.terminate()
            self.process.wait()
            self.process = None
            print("Bluetooth receiver stopped.")

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
box_info = load_box_info()
BOX_ID = int(box_info["BOX_ID"])
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
bluetooth_manager = BluetoothManager()

def run_script(script_name, background=False):
    try:
        print(f"Running {script_name} {'(background)' if background else ''}...")
        if background:
            subprocess.Popen(['python3', os.path.expanduser(f"~/Desktop/{script_name}")])
        else:
            subprocess.run(['python3', os.path.expanduser(f"~/Desktop/{script_name}")])
    except Exception as e:
        print(f"Error while running {script_name}: {e}")

def handle_authorized_card(card_id):
    global box_open
    print(f"Carte scannée : {card_id}")
    authorized_ids = load_authorized_ids()
    if card_id in authorized_ids:
        if box_open:
            print("Carte reconnue. Fermeture du servo.")
            run_script("ServoClose.py")
            if led_init_success and led_vert: led_vert.off()
            stop_blinking_red_led()
            if led_init_success and led_rouge: led_rouge.on()
            print("LED rouge allumée (servo fermé), LED verte éteinte.")
            box_open = False
        else:
            print("Carte reconnue. Ouverture du servo.")
            run_script("ServoOpen.py")
            if led_init_success and led_vert: led_vert.on()
            stop_blinking_red_led()
            if led_init_success and led_rouge: led_rouge.off()
            print("LED verte allumée (servo ouvert), LED rouge éteinte.")
            box_open = True
    else:
        print("Carte non autorisée.")

def listen_for_rfid(callback):
    def decode(raw_bytes):
        key_map = {
            30: '1', 31: '2', 32: '3', 33: '4', 34: '5',
            35: '6', 36: '7', 37: '8', 38: '9', 39: '0'
        }
        return key_map.get(raw_bytes[2], None)

    print("Lecture du lecteur RFID via /dev/hidraw0...")
    card = ""
    try:
        with open(HID_PATH, 'rb') as f:
            while True:
                r = f.read(8)
                val = decode(r)
                if val:
                    card += val
                if r[2] == 40 and card:
                    callback(card)
                    card = ""
    except Exception as e:
        print(f"Erreur HID : {e}")

threading.Thread(target=listen_for_rfid, args=(handle_authorized_card,), daemon=True).start()

# Vérifier les commandes Supabase
def check_and_execute():
    response = supabase.table("commands") \
        .select("*") \
        .eq("is_executed", False) \
        .eq("box_id", BOX_ID) \
        .order("created_at") \
        .execute()

    if response.data:
        for cmd in response.data:
            command = cmd['command']
            print(f"Received command: {command}")

            if command == "buzzer":
                run_script("BuzzerStart.py", background=True)
            elif command == "stop_buzzer":
                run_script("BuzzerStop.py")
            elif command == "led":
                run_script("LedOn.py", background=True)
            elif command == "stop_led":
                run_script("LedOff.py")
            elif command == "open_servo":
                run_script("ServoOpen.py")
                if led_init_success and led_vert: led_vert.on()
                stop_blinking_red_led()
                if led_init_success and led_rouge: led_rouge.off()
                print("LED verte allumée (servo ouvert), LED rouge éteinte.")
            elif command == "close_servo":
                run_script("ServoClose.py")
                if led_init_success and led_vert: led_vert.off()
                stop_blinking_red_led()
                if led_init_success and led_rouge: led_rouge.on()
                print("LED rouge allumée (servo fermé), LED verte éteinte.")
            elif command == "temp":
                run_script("TempStart.py", background=True)
            elif command == "stop_temp":
                run_script("TempStop.py")
            elif command == "start_bluetooth":
                bluetooth_manager.start()
            elif command == "stop_bluetooth":
                bluetooth_manager.stop()
            else:
                print(f"Unknown command: {command}")

            supabase.table("commands").update({"is_executed": True}).eq("id", cmd["id"]).execute()

# Point d'entrée principal
if __name__ == "__main__":
    start_bluetooth_adapter()

    wifi_connected_last_check = is_wifi_connected()
    if wifi_connected_last_check:
        print("Wi-Fi and Internet detected, proceeding to listen for commands...")
        stop_blinking_red_led()
    else:
        print("No Internet detected! Trying to find another Wi-Fi...")
        if not scan_and_connect_wifi():
            print("Switching to Bluetooth Receiver mode...")
            bluetooth_manager.start()
            start_blinking_red_led()

    print(f" Listening for commands for Box ID {BOX_ID}...")

    while True:
        current_wifi_connected = is_wifi_connected()

        if wifi_connected_last_check and not current_wifi_connected:
            print("Lost Internet connection! Trying other Wi-Fi...")
            if not scan_and_connect_wifi():
                print("No working Wi-Fi found. Starting Bluetooth Receiver...")
                bluetooth_manager.start()
                start_blinking_red_led()
            else:
                print("Connected to new Wi-Fi. Bluetooth not needed.")
                bluetooth_manager.stop()
                stop_blinking_red_led()

        elif not wifi_connected_last_check and current_wifi_connected:
            print("Internet connection restored! Stopping Bluetooth Receiver...")
            bluetooth_manager.stop()
            stop_blinking_red_led()

        wifi_connected_last_check = current_wifi_connected

        if current_wifi_connected:
            check_and_execute()
        else:
            print("No Internet - Skipping Supabase checks... Waiting...")

        time.sleep(1)