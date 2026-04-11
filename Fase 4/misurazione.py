"""
misurazione.py

Modulo locale per la rilevazione di temperatura e umidità
tramite sensore DHT11.

Importa i parametri di configurazione dal file configurazione.json

Restituisce un IOTdata conforme alle specifiche.
"""

import json                 # libreria per leggere file JSON
import dht                  # libreria per gestire il sensore DHT11
import time
from machine import Pin     # libreria per gestire il GPIO su ESP32/ESP8266

# contatore globale delle rilevazioni
contatore_rilevazioni = 0


def carica_configurazione():
    """
    Carica il file configurazione.json.
    Gestisce eventuali errori di apertura o formato.
    """
    try:
        with open("configurazione.json", "r") as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        raise RuntimeError("File configurazione.json non trovato")
    except json.JSONDecodeError:
        raise RuntimeError("Errore nel formato JSON")


def crea_sensore(config):
    """
    Crea il sensore DHT11 usando il pin definito nel JSON.
    """
    try:
        pin_segnale = config["cablaggio"]["segnale"]
        pin = Pin(pin_segnale, Pin.IN)  # Pin per lettura
        return dht.DHT11(pin)
    #eccezione generata quando si tenta di accedere a una chiave inesistente in un dizionario Python
    except KeyError:
        raise RuntimeError("Errore nei parametri di cablaggio")


def effettua_misurazione():
    """
    Effettua una rilevazione completa e costruisce l'IOTdata.
    """

    global contatore_rilevazioni

    try:
        config = carica_configurazione()
        sensore = crea_sensore(config)

        # lettura del sensore
        sensore.measure()
        temperatura = sensore.temperature()
        umidita = sensore.humidity()

        if temperatura is None or umidita is None:
            raise RuntimeError("Errore lettura sensore")

        # incremento numero rilevazione
        contatore_rilevazioni += 1

        # timestamp corrente
        timestamp = int(time.time())

        # costruzione IOTdata
        iotdata = {
            "camera": config["camera"],
            "ponte": config["ponte"],
            "sensore": config["sensore"],
            "identita": config["identita"],
            "osservazione": {
                "rilevazione": contatore_rilevazioni,
                "temperatura": round(temperatura, 2),
                "umidita": round(umidita, 2)
            },
            "dataeora": timestamp
        }

        return iotdata

    except Exception as e:
        # condivide l'errore verso dc.py
        raise RuntimeError(f"Errore durante la misurazione: {e}")  # f serve a creare una stringa formattata


# debug locale
if __name__ == "__main__":
    try:
        dato = effettua_misurazione()
        print("IOTdata generato:")
        print(dato)
    except RuntimeError as errore:
        print("ERRORE:", errore)