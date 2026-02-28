'''
iotgwda.py
Server TCP DA/GIOT che riceve gli IOTdata dal DC tramite socket TCP/IP,
Calcola la media di temperatura e umidità
Ogni TEMPO_INVIO secondi genera un nuovo IOTdata del DA
Passa il dato al modulo cripto
Salva i dati su file iotp/db.json
'''

import socket        # gestione comunicazione TCP/IP
import json          # gestione dati in formato JSON
import time          # gestione timestamp e intervalli temporali
import cripto        # modulo locale per la criptazione

# lettura paramentri da file parametri.conf che contiene configurazioni del DA
with open('parametri.json', 'r', encoding='utf-8') as conf_file:    # apertura file configurazione
config = json.load(conf_file)                # lettura parametri

# Assegnazione parametri
TEMPO_RILEVAZIONE = config["TEMPO_RILEVAZIONE"]
TEMPO_INVIO = config["TEMPO_INVIO"]     #in secondi
N_DECIMALI = config["N_DECIMALI"]
IDENTITA_GIOT = config["IDENTITA_GIOT"]
IP_SERVER = config["IP_SERVER"]
PORTA_SERVER = config["PORTA_SERVER"]

#inizializzazione variabili per i calcoli
somma_temperatura = 0
somma_umidita = 0
conteggio = 0

ultimo_invio = time.time() # memorizza il momento dell’ultimo invio
invio_numero = 0           # conta quanti invii sono stati fatti alla IoT Platform

# Creazione socket server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creazione (socket.AF_INET per IPv4 e socket.SOCK_STREAM per TCP)
server.bind((IP_SERVER, PORTA_SERVER)) # associa porta e ip
server.listen(1)                 #server in ascolto accettando 1 client alla volta

print("Server DA/GIOT avviato")
print("In ascolto su", IP_SERVER, "porta", PORTA_SERVER)

try:
    while True:
        # Attesa connessione DC
        connessione, indirizzo = server.accept()
        print("DC connesso:", indirizzo)

        #DA comunica al DC ogni quanto inviare i dati
        connessione.send(str(TEMPO_RILEVAZIONE).encode()) #encode trasforma stringa in byte

        while True:
            dati = connessione.recv(4096) #4096 n max byte che si possono ricevre in una volta
            if not dati:
                break

            # ricezione dati, decodificati e convertiti in dizionario Python
            dato_dc = json.loads(dati.decode()) #decode() trasforma i byte in stringa

            print("Dato ricevuto dal DC:")
            print(json.dumps(dato_dc, indent=4)) #json.dumps() trasforma oggetto Python in una stringa JSON

            # Estrazione dati dal JSON ricevuto
            temperatura = dato_dc["osservazione"]["temperatura"]
            umidita = dato_dc["osservazione"]["umidita"]
            camera = dato_dc["camera"]
            ponte = dato_dc["ponte"]

            # Aggiornamento somme e conteggio
            somma_temperatura += temperatura
            somma_umidita += umidita
            conteggio += 1

            # Controllo tempo di invio 
            if time.time() - ultimo_invio >= TEMPO_INVIO and conteggio > 0:
                ultimo_invio = time.time()
                invio_numero += 1

                # Calcolo delle medie 
                media_temperatura = round(somma_temperatura / conteggio, N_DECIMALI)
                media_umidita = round(somma_umidita / conteggio, N_DECIMALI)

                # Costruzione IOTdata del DA 
                dato_da = {
                    "camera": camera,
                    "ponte": ponte,
                    "temperaturam": media_temperatura,
                    "umiditam": media_umidita,
                    "dataeora": int(time.time()),
                    "invionumero": invio_numero,
                    "identita": IDENTITA_GIOT
                }

                # Conversione in JSON
                dato_json = json.dumps(dato_da)

                # criptazione dati
                dato_criptato = cripta.cripto(dato_json)

                print("Dato inviato alla IoT Platform (criptato):")
                print(dato_criptato)

                # Salvataggio su archivio locale (db.json)
                with open('iotp/db.json', 'a') as file: #apertura file in append
                    file.write(dato_json + "\n") #scrittura dati

                # Reset delle variabili per il prossimo ciclo
                somma_temperatura = 0
                somma_umidita = 0
                conteggio = 0

# Terminazione con CTRL+C
except KeyboardInterrupt:
    print("\nChiusura del server")
    print("Numero totale invii alla IoT Platform:", invio_numero)

#chiusura socket
finally:
    server.close()
    print("Socket server chiuso")
