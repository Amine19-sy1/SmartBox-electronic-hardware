import time
import subprocess
import os
from dotenv import load_dotenv
from supabase import create_client

# Charger les variables d'environnement
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BOX_ID = 1

# Connexion à Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def run_script(script_name):
    try:
        print(f"Running {script_name}...")
        subprocess.run(['python3', script_name])
    except Exception as e:
        print(f"Error while running {script_name}: {e}")

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
                run_script("Buzzer.py")
            elif command == "led":
                run_script("Led.py")
            elif command == "servo":
                run_script("Servo.py")
            elif command == "temp":
                run_script("TempLogger.py")
            else:
                print(f"Unknown command: {command}")

            # Marquer la commande comme exécutée
            supabase.table("commands").update({"is_executed": True}).eq("id", cmd["id"]).execute()

if __name__ == "__main__":
    print(f"Listening for commands for Box ID {BOX_ID}...")
    while True:
        check_and_execute()
        time.sleep(5)  # Vérifie toutes les 5 secondes
