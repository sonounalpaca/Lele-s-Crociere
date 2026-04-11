"""
wifidc.py
Modulo per la connessione WiFi del Data Collector (Raspberry Pico W)
Legge le credenziali dal file wifipico.json
"""

import network
import rp2
import time
import json


# Lettura credenziali WiFi
def leggi_credenziali():
    conf_file = open('wifipico.json', 'r')
    config = json.load(conf_file)
    conf_file.close()

    SSID = config["ssid"]
    PASSWORD = config["pw"]

    return SSID, PASSWORD


# Connessione alla rete WiFi
def connetti_wifi(timeout=15):

    # Impostazione paese (evita problemi canali WiFi)
    rp2.country('IT')

    # Creazione interfaccia WiFi in modalità Station
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Recupero credenziali
    SSID, PASSWORD = leggi_credenziali()

    print("Connessione alla rete:", SSID)
    wlan.connect(SSID, PASSWORD)

    # Attesa connessione
    start = time.time()

    while not wlan.isconnected():
        if time.time() - start > timeout:
            print("Errore: timeout connessione WiFi")
            return None
        time.sleep(1)

    # Connessione riuscita
    print("Connessione WiFi riuscita")

    stato = wlan.ifconfig()
    IP_ASSEGNATO = stato[0]

    print("IP Pico:", IP_ASSEGNATO)

    return IP_ASSEGNATO