import RPi.GPIO as GPIO
import dht11
import time
import signal
import sys
import os
import subprocess
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialiser GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Lire BOX_ID depuis Boxinfo.txt
def get_box_id():
    try:
        with open("/home/amine/Desktop/Boxinfo.txt", "r") as f:
            for line in f:
                if line.startswith("BOX_ID="):
                    return int(line.strip().split("=")[1])
    except Exception as e:
        print(f"Failed to read Box ID: {e}")
    return None

# Gestion propre de l’arrêt
def handle_exit(signum, frame):
    print("Exiting... Cleaning GPIO")
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# Lire l’identifiant de la box
box_id = get_box_id()
if box_id is None:
    print("No BOX_ID found. Exiting.")
    sys.exit(1)

# Initialisation du capteur DHT11 sur GPIO 23
instance = dht11.DHT11(pin=23)
print(" Starting DHT11 reading on GPIO 23...")

# Lire jusqu'à obtenir une lecture valide (boucle infinie avec arrêt conditionnel)
while True:
    result = instance.read()
    if result.is_valid():
        temp = round(float(result.temperature), 2)
        hum = int(result.humidity)
        print(f"Temperature: {temp}°C, Humidity: {hum}%")

        try:
            supabase.table("temperature").insert({
                "temperature": temp,
                "humidity": hum,
                "box_id": box_id
            }).execute()
            print("Data sent to Supabase.")
        except Exception as e:
            print(f"Failed to insert data: {e}")
        break
    else:
        print("Read failed. Retrying in 1 second...")
        time.sleep(1)

# Nettoyer GPIO
GPIO.cleanup()

# Appeler TempStop.py automatiquement
try:
    subprocess.run(["python3", "/home/amine/Desktop/TempStop.py"])
except Exception as e:
    print(f"Failed to run TempStop.py: {e}")
