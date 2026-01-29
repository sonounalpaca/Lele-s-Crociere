'''
iotgwda.py
Server TCP DA/GIOT che riceve dati IoT dai DC,
li elabora e li invia (simulazione) alla IoT Platform
'''

import socket        # per la comunicazione TCP
import json          # per gestire dati JSON
import time          # per gestire tempi e pause
import cripta        # per la criptazione 

# lettura paramentri da file parametri.conf che contiene configurazioni del DA
conf_file = open("parametri.conf", "r")      # apertura file configurazione
config = json.load(conf_file)                # lettura parametri
conf_file.close()                            # chiusura file

# Assegnazione parametri
TEMPO_RILEVAZIONE = config["TEMPO_RILEVAZIONE"]
TEMPO_INVIO = config["TEMPO_INVIO"] * 60     #conversione da min a sec perchè time.time() lavora in secondi
N_DECIMALI = config["N_DECIMALI"]
IDENTITA_GIOT = config["IDENTITA_GIOT"]
IP_SERVER = config["IP_SERVER"]
PORTA_SERVER = config["PORTA_SERVER"]

somma_temperatura = 0
somma_umidita = 0
conteggio = 0

ultimo_invio = time.time()       # memorizza il momento dell’ultimo invio dei dati alla IoT Platform
invio_numero = 0                 # numero invii di DA alla IoT Platform

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

            # ricezione dati, decodificati e convertiti in Python
            dato_dc = json.loads(dati.decode()) #json.loads() converte stringa JSON in un oggetto Python e decode() trasforma i byte in stringa

            print("Dato ricevuto dal DC:")
            print(json.dumps(dato_dc, indent=4)) #json.dumps() trasforma oggetto Python in una stringa JSON

            # Aggiornamento somme
            somma_temperatura += dato_dc["osservazione"]["temperatura"]
            somma_umidita += dato_dc["osservazione"]["umidita"]
            conteggio += 1

            # Controllo tempo di invio 
            if time.time() - ultimo_invio >= TEMPO_INVIO:
                ultimo_invio = time.time()
                invio_numero += 1

                # Calcolo medie
                media_temperatura = round(somma_temperatura / conteggio, N_DECIMALI)
                media_umidita = round(somma_umidita / conteggio, N_DECIMALI)

                # Creazione DatoIoT DA
                dato_iot_giot = {
                    "identita_giot": IDENTITA_GIOT,
                    "invionumero": invio_numero,
                    "media_temperatura": media_temperatura,
                    "media_umidita": media_umidita
                }

                # Conversione in JSON
                dato_iot_json = json.dumps(dato_iot_giot)

                # criptazione dati
                dato_iot_json_criptato = cripta.criptazione(dato_iot_json)

                print("Dato inviato alla IoT Platform (criptato):")
                print(dato_iot_json_criptato)

                # Salvataggio su file IoT Platform
                file_iotp = open("../IOTP/iotdata.dbt", "a") #apre file in append
                file_iotp.write(dato_iot_json + "\n") #scrive dati
                file_iotp.close() #chiude file

                # Reset variabili
                somma_temperatura = 0
                somma_umidita = 0
                conteggio = 0

# Terminazione con CTRL+C
except KeyboardInterrupt:
    print("\nChiusura del server")
    print("Numero totale invii alla IoT Platform:", invio_numero)

finally:
    server.close()
    print("Socket server chiuso")
