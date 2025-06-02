# Desktop/TempStop.py
import os
import signal
import subprocess
import time

def kill_tempstart_script():
    try:
        # Trouver le processus TempStart.py
        output = subprocess.check_output(["pgrep", "-f", "TempStart.py"]).decode().strip()
        if output:
            pids = output.split("\n")
            for pid in pids:
                print(f"Killing TempStart.py process with PID {pid}")
                os.kill(int(pid), signal.SIGTERM)
                time.sleep(1)  # attendre un peu pour libérer GPIO
    except subprocess.CalledProcessError:
        print("No TempStart.py process found.")

if __name__ == "__main__":
    kill_tempstart_script()
    print("Temperature reading stopped and GPIO freed.")
