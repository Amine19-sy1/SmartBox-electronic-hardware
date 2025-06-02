HID_PATH = "/dev/hidraw0"

def decode(raw_bytes):
    """Décoder les données brutes HID en chiffres (standard AZERTY/US)"""
    # Tableau HID pour chiffres (clavier US)
    key_map = {
        30: '1', 31: '2', 32: '3', 33: '4', 34: '5',
        35: '6', 36: '7', 37: '8', 38: '9', 39: '0'
    }
    return key_map.get(raw_bytes[2], None)

print("Lecture du lecteur RFID via /dev/hidraw0... Passe une carte.")

card = ""
with open(HID_PATH, 'rb') as f:
    while True:
        r = f.read(8)
        val = decode(r)
        if val:
            card += val
            print(val, end="", flush=True)
        if r[2] == 40:  # touche Entrée
            print(f"\nID complet : {card}")
            card = ""
