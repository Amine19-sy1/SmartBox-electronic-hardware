import bluetooth

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]
bluetooth.advertise_service(server_sock, "WifiConfigServer",
                            service_classes=[bluetooth.SERIAL_PORT_CLASS],
                            profiles=[bluetooth.SERIAL_PORT_PROFILE])

print(f"Waiting for connection on RFCOMM channel {port}")

client_sock, client_info = server_sock.accept()
print(f"Accepted connection from {client_info}")

try:
    data = client_sock.recv(1024).decode('utf-8')
    print(f"Received: {data}")
    
    import json
    wifi_data = json.loads(data)
    ssid = wifi_data['ssid']
    password = wifi_data['password']

    # Update Wi-Fi config
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as f:
        f.write(f'''
network={{
    ssid="{ssid}"
    psk="{password}"
}}
''')
    # Restart the network service
    import subprocess
    subprocess.run(["wpa_cli", "-i", "wlan0", "reconfigure"])

    client_sock.send("✅ Wi-Fi credentials received successfully.")
finally:
    client_sock.close()
    server_sock.close()
