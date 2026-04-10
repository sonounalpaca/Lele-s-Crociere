"""
archivia_iotp.py
IoT Platform - Fase 4

Subscriber MQTT che:
1. Si connette al broker MQTT
2. Riceve dati IoT criptati dai gateway
3. Decripta i dati con cripto.py
4. Archivia su dbplatform.json
"""

import json
import paho.mqtt.client as mqtt
import cripto


# LETTURA CONFIGURAZIONE IOTP
conf_file = open("iotp/iotp.json", "r")
config = json.load(conf_file)
conf_file.close()

TOPIC = config["topic"]
BROKER_HOST = config["broker"]["host"]
PORTA_BROKER = config["broker"]["porta"]
DB_FILE = "iotp/" + config["dbfile"]["file"]
MODO = config["dbfile"]["modo"]

KEEPALIVE = 60


# CALLBACK CONNESSIONE
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connesso al broker MQTT")
        print("Broker:", BROKER_HOST, "Porta:", PORTA_BROKER)
        print("Topic:", TOPIC)
        print()

        client.subscribe(TOPIC)

    else:
        print("Connessione fallita")


# CALLBACK MESSAGGIO RICEVUTO
def on_message(client, userdata, msg):
    try:
        # Messaggio ricevuto (criptato)
        dato_criptato = msg.payload.decode()

        # Decriptazione
        dato_decriptato = cripto.decripta(dato_criptato)

        # Conversione JSON
        dato_json = json.loads(dato_decriptato)

        # DEBUG
        print("Dato ricevuto:")
        print(json.dumps(dato_json, indent=4))
        print()

        # Archiviazione su file
        with open(DB_FILE, MODO) as f:
            f.write(json.dumps(dato_json))
            f.write("\n")

    except Exception as e:
        print("Errore ricezione:", e)


# MAIN
client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

print("Avvio IoT Platform subscriber...")
print("In attesa dati...\n")

client.connect(BROKER_HOST, PORTA_BROKER, KEEPALIVE)

try:
    client.loop_forever()

except KeyboardInterrupt:
    print("\nChiusura subscriber")