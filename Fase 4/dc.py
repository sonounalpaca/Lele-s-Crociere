"""
dc.py
Data Collector - Fase 3

Client TCP su Raspberry Pico che:
1. Si connette al WiFi
2. Si collega al DA
3. Invia dati IoT periodicamente
"""

import socket
import json
import time
import misurazione
import wifidc


# CONNESSIONE WIFI
print("Connessione alla rete WiFi...")
ip_locale = wifidc.connetti_wifi()

if ip_locale is None:
    print("Impossibile connettersi al WiFi")
    raise SystemExit

print("WiFi connesso. IP assegnato:", ip_locale)


# LETTURA CONFIGURAZIONE DC
conf_file = open('configurazionedc.conf', 'r')
config = json.load(conf_file)
conf_file.close()

CABINA = config["Cabina"]
PONTE = config["Ponte"]
SENSORE = config["Sensore"]
IDENTITA = config["Identità"]
IP_SERVER = config["IPServer"]
PORTA_SERVER = config["PortaServer"]


# CREAZIONE SOCKET CLIENT
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    print("Connessione al DA...")
    client_socket.connect((IP_SERVER, PORTA_SERVER))
    print("Connesso al DA")

    # Ricezione tempo di rilevazione dal DA
    data = client_socket.recv(1024).decode()
    TEMPO_RILEVAZIONE = int(data)
    print("Tempo di rilevazione ricevuto:", TEMPO_RILEVAZIONE, "secondi")

    # Contatore rilevazioni
    n_rilevazione = 0

    # CICLO PRINCIPALE
    while True:
        n_rilevazione += 1

        # Lettura dati sensore
        temperatura = misurazione.on_temperatura(SENSORE["ErroreT"])
        umidita = misurazione.on_umidita(SENSORE["ErroreU"])

        # Creazione struttura DatoIoT
        dato_iot = {
            "cabina": CABINA,
            "ponte": PONTE,
            "identita": IDENTITA,
            "sensore": {
                "nome": SENSORE["Nome"],
                "tmin": SENSORE["Tmin"],
                "tmax": SENSORE["Tmax"],
                "umin": SENSORE["Umin"],
                "umax": SENSORE["Umax"],
                "erroret": SENSORE["ErroreT"],
                "erroreu": SENSORE["ErroreU"]
            },
            "osservazione": {
                "rilevazione": n_rilevazione,
                "temperatura": temperatura,
                "umidita": umidita,
                "timestamp": time.time()
            }
        }

        # Conversione in JSON
        dato_json = json.dumps(dato_iot)

        # Invio al DA
        client_socket.send(dato_json.encode())

        # Debug
        print("Dato inviato:")
        print(json.dumps(dato_iot, indent=4))

        # Attesa prima della prossima rilevazione
        time.sleep(TEMPO_RILEVAZIONE)


# GESTIONE ERRORI
except KeyboardInterrupt:
    print("\nChiusura DC...")

except Exception as e:
    print("Errore:", e)

finally:
    client_socket.close()
    print("Socket chiuso")