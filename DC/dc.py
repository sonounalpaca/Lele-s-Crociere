"""
dc.py
Client TCP che invia dati IoT al DA
"""

import socket
import json
import time
import misurazione

# Lettura configurazione DC
conf_file = open('configurazionedc.conf', 'r')
config = json.load(conf_file)
conf_file.close()

CABINA = config["Cabina"]
PONTE = config["Ponte"]
SENSORE = config["Sensore"]
IDENTITA = config["Identità"]
IP_SERVER = config["IPServer"]
PORTA_SERVER = config["PortaServer"]

# Creazione socket client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    print("Connessione al DA...")
    client_socket.connect((IP_SERVER, PORTA_SERVER))
    print("Connesso al DA")

    # Ricezione TEMPO_RILEVAZIONE dal DA
    data = client_socket.recv(1024).decode()
    TEMPO_RILEVAZIONE = int(data)
    print("Tempo di rilevazione ricevuto:", TEMPO_RILEVAZIONE, "secondi")

    # Inizializzazione contatore rilevazioni
    n_rilevazione = 0

    # Ciclo di rilevazione
    while True:
        n_rilevazione += 1

        temperatura = misurazione.on_temperatura(SENSORE["ErroreT"])
        umidita = misurazione.on_umidita(SENSORE["ErroreU"])

        # Creazione DatoIoT
        dato_iot = {
            "cabina": CABINA,
            "ponte": PONTE,
            "sensore": {
                "nome": SENSORE["Nome"],
                "tmin": SENSORE["Tmin"],
                "tmax": SENSORE["Tmax"],
                "umin": SENSORE["Umin"],
                "umax": SENSORE["Umax"],
                "erroret": SENSORE["ErroreT"],
                "erroreu": SENSORE["ErroreU"]
            },
            "identita": IDENTITA,
            "osservazione": {
                "rilevazione": n_rilevazione,
                "temperatura": temperatura,
                "umidita": umidita
            }
        }

        # Conversione in JSON
        dato_json = json.dumps(dato_iot)

        # Invio al DA
        client_socket.send(dato_json.encode())

        # Visualizzazione a video
        print("Dato inviato:")
        print(json.dumps(dato_iot, indent=4))

        # Attesa prima dell'invio di nuovi dati
        time.sleep(TEMPO_RILEVAZIONE)

# Gestione CTRL+C
except KeyboardInterrupt:
    print("\nChiusura DC...")

except Exception as e:
    print("Errore:", e)

finally:
    client_socket.close()
    print("Socket chiuso")

