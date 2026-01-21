"""
simulaiotdata.py
FASE 1: simulazione acquisizione e salvataggio dati IoT
"""

import time
import random
import json
import misurazione

# Lettura parametri di configurazione
param_file = open("configurazione/parametri.conf", "r", encoding="utf-8")
parametri = json.load(param_file)
param_file.close()

TEMPO_RILEVAZIONE = parametri["TEMPO_RILEVAZIONE"]
N_DECIMALI = parametri["N_DECIMALI"]
N_CABINE = parametri["N_CABINE"]
N_PONTI = parametri["N_PONTI"]

# Inizializzazioni
nRilevazione = 0
somma_temp = 0
somma_umid = 0

# Ciclo di rilevazione
try:
    while True:

        # Apertura file in append 
        json_file = open("dati/iotdata.dbt", "a")

        # Generazione dati
        nCabina = random.randint(1, N_CABINE)
        nPonte = random.randint(1, N_PONTI)
        nRilevazione += 1

        TS = time.time()

        temp = misurazione.on_temperatura(N_DECIMALI)
        umid = misurazione.on_umidita(N_DECIMALI)

        # Calcolo delle somme per media finale dei dati
        somma_temp += temp
        somma_umid += umid

        # Creazione DatoIoT
        Dati = {
            "Cabina": nCabina,
            "Ponte": nPonte,
            "Rilevazione": nRilevazione,
            "Data e Ora": TS,
            "Temperatura": temp,
            "Umidità": umid
        }

        # Visualizzazione a video
        print(json.dumps(Dati, indent=4))

        # Scrittura su file
        json.dump(Dati, json_file, indent=4)
        json_file.write("\n")

        # Chiusura file
        json_file.close()

        # Attesa
        time.sleep(TEMPO_RILEVAZIONE)

# Gestione fine ciclo con CTRL+C
except KeyboardInterrupt:

    print("\n--- TERMINAZIONE RILEVAZIONE ---")

    if nRilevazione > 0:
        media_temp = round(somma_temp / nRilevazione, N_DECIMALI)
        media_umid = round(somma_umid / nRilevazione, N_DECIMALI)
    else:
        media_temp = 0
        media_umid = 0

    print("Numero rilevazioni:", nRilevazione)
    print("Temperatura media:", media_temp)
    print("Umidità media:", media_umid)
