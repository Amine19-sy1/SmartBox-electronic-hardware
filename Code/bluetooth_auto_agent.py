#!/usr/bin/env python3

import subprocess
import time
import pexpect
import os

def setup_bluetooth_daemon():
    print(" Restarting bluetoothd with compatibility and SDP enabled...")

    # Stop system-managed bluetooth service
    subprocess.run(["sudo", "systemctl", "stop", "bluetooth"])
    subprocess.run(["sudo", "systemctl", "disable", "bluetooth"])
    subprocess.run(["sudo", "pkill", "bluetoothd"])

    # Launch bluetoothd manually in background
    subprocess.Popen(
        ["sudo", "/usr/libexec/bluetooth/bluetoothd", "--debug", "--compat", "--noplugin=sap"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    time.sleep(2)  # Wait for bluetoothd to be ready

    # Add Serial Port Profile (RFCOMM)
    subprocess.run(["sudo", "sdptool", "add", "SP"])
    print("bluetoothd launched and SP profile added.")

def start_bluetoothctl_agent():
    print("Starting Bluetooth Agent...")

    child = pexpect.spawn("bluetoothctl", encoding='utf-8', timeout=10)
    child.logfile_read = open("bluetooth_debug.log", "w")

    try:
        child.expect("#")
        child.sendline("power on")
        child.expect("#")
        child.sendline("agent on")
        child.expect("#")
        child.sendline("default-agent")
        child.expect("#")
        child.sendline("discoverable on")
        child.expect("#")
        child.sendline("pairable on")

        print("Agent is active. Waiting for devices...")

        while True:
            idx = child.expect([
                r"Confirm passkey \d+ \(yes/no\):",
                r"Authorize service [0-9a-f\-]+ \(yes/no\):",
                pexpect.TIMEOUT,
                pexpect.EOF
            ], timeout=None)

            if idx == 0:
                print(" Confirming passkey...")
                child.sendline("yes")
            elif idx == 1:
                print("Authorizing service...")
                child.sendline("yes")

    except Exception as e:
        print(f"Exception in agent: {e}")

if __name__ == "__main__":
    setup_bluetooth_daemon()
    start_bluetoothctl_agent()
