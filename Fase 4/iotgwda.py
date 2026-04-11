'''
iotgwda.py
Server TCP DA/GIOT che riceve gli IOTdata dal DC tramite socket TCP/IP,
calcola la media di temperatura e umidità,
ogni TEMPO_INVIO secondi genera un nuovo IOTdata del DA,
lo cripta e lo pubblica sul broker MQTT.
'''

import socket        # gestione comunicazione TCP/IP
import json          # gestione dati in formato JSON
import time          # gestione timestamp e intervalli temporali
import cripto        # modulo locale per la criptazione
import paho.mqtt.client as mqtt   # libreria MQTT

# Lettura parametri da file parametri.json
with open('configurazione/parametri.json', 'r', encoding='utf-8') as conf_file:
    config = json.load(conf_file)

# Assegnazione parametri
TEMPO_RILEVAZIONE = config["TEMPO_RILEVAZIONE"]
TEMPO_INVIO       = config["TEMPO_INVIO"]       # in secondi
N_DECIMALI        = config["N_DECIMALI"]
IDENTITA_GIOT     = config["IDENTITA_GIOT"]
IP_SERVER         = config["IP_SERVER"]
PORTA_SERVER      = config["PORTA_SERVER"]
TOPIC             = config["TOPIC"]
BROKER            = config["BROKER"]
PORTA_BROKER      = config["PORTA_BROKER"]

# Inizializzazione variabili calcolo
somma_temperatura = 0
somma_umidita     = 0
conteggio         = 0
ultimo_invio      = time.time()
invio_numero      = 0

# Connessione al broker MQTT
client_mqtt = mqtt.Client()
client_mqtt.connect(BROKER, PORTA_BROKER, 60)
client_mqtt.loop_start()

print("Server DA/GIOT avviato")
print("In ascolto su", IP_SERVER, "porta", PORTA_SERVER)
print("MQTT broker:", BROKER, "porta:", PORTA_BROKER)
print("Topic:", TOPIC)

# Creazione socket server TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP_SERVER, PORTA_SERVER))
server.listen(1)

try:
    while True:
        # Attesa connessione DC
        connessione, indirizzo = server.accept()
        print("DC connesso:", indirizzo)

        # Comunica al DC ogni quanto inviare i dati
        connessione.send(str(TEMPO_RILEVAZIONE).encode())

        while True:
            print("Gateway IoT in attesa di dati")
            dati = connessione.recv(4096)
            if not dati:
                break

            print("Gateway IoT in ricezione e invio")

            # Decodifica e conversione in dizionario Python
            dato_dc = json.loads(dati.decode())

            # Debug: stampa dato non criptato ricevuto dal DC
            print("Dato ricevuto dal DC:")
            print(json.dumps(dato_dc, indent=4))

            # Estrazione dati
            temperatura = dato_dc["osservazione"]["temperatura"]
            umidita     = dato_dc["osservazione"]["umidita"]
            cabina      = dato_dc["cabina"]
            ponte       = dato_dc["ponte"]

            # Aggiornamento somme
            somma_temperatura += temperatura
            somma_umidita     += umidita
            conteggio         += 1

            # Controllo tempo di invio
            if time.time() - ultimo_invio >= TEMPO_INVIO and conteggio > 0:
                ultimo_invio  = time.time()
                invio_numero += 1

                # Calcolo medie
                media_temperatura = round(somma_temperatura / conteggio, N_DECIMALI)
                media_umidita     = round(somma_umidita     / conteggio, N_DECIMALI)

                # Costruzione DatoIoT
                dato_da = {
                    "cabina":       cabina,
                    "ponte":        ponte,
                    "temperaturam": media_temperatura,
                    "umiditam":     media_umidita,
                    "dataeora":     int(time.time()),
                    "invionumero":  invio_numero,
                    "identita":     IDENTITA_GIOT
                }

                # Conversione in stringa JSON
                dato_json = json.dumps(dato_da)

                # Criptazione
                dato_criptato = cripto.criptazione(dato_json)

                # Pubblicazione sul broker MQTT
                client_mqtt.publish(TOPIC, dato_criptato)

                print("Dato pubblicato su MQTT (criptato):")
                print(dato_criptato)
                print()

                # Reset variabili
                somma_temperatura = 0
                somma_umidita     = 0
                conteggio         = 0

# Terminazione con CTRL+C
except KeyboardInterrupt:
    print("\nChiusura del server")
    print("Numero totale invii alla IoT Platform:", invio_numero)

finally:
    client_mqtt.loop_stop()
    client_mqtt.disconnect()
    server.close()
    print("Socket server chiuso")
