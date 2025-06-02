from gpiozero import LED
import time

# Déclaration de la LED bleue (GPIO 24)
led_bleue = LED(24)

print(" Clignotement de la LED bleue pendant 5 secondes [CTRL+C pour arrêter]")

# Durée totale du clignotement
duree_totale = 5  # secondes
delai_clignotement = 0.5  # ON/OFF toutes les 0.5 secondes
debut = time.time()

try:
    while time.time() - debut < duree_totale:
        led_bleue.on()
        time.sleep(delai_clignotement)
        led_bleue.off()
        time.sleep(delai_clignotement)

    print("Fin du clignotement.")
    led_bleue.off()

except KeyboardInterrupt:
    print("Interruption par l'utilisateur.")
    led_bleue.off()
