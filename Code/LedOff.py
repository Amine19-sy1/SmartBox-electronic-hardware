# Desktop/LedOff.py
import os
import signal
import subprocess
import time

def kill_ledon_script():
    # Trouver le processus LedOn.py
    try:
        output = subprocess.check_output(["pgrep", "-f", "LedOn.py"]).decode().strip()
        if output:
            pids = output.split("\n")
            for pid in pids:
                print(f"Killing LedOn.py process with PID {pid}")
                os.kill(int(pid), signal.SIGTERM)
                time.sleep(1)  # attendre un peu que GPIO se libère
    except subprocess.CalledProcessError:
        print("No LedOn.py process found.")

if __name__ == "__main__":
    kill_ledon_script()
    print("LED stopped and GPIO freed.")
