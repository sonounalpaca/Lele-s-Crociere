"""
simulationdata.py
FASE 1: struttura del sistema di acquisizione e salvataggio dati
I dati verranno forniti nella fase 2 dal sistema server-client
"""


import time                             
import random                            
import json
import datetime

nRilevazione = 1 # Varialibe che va ad incrementarsi ogni volta che viene effettuata una rilevazione

while (True):
    # File in modalità append (i nuovi dati vengono quindi aggiunti alla fine del file ogni volta, senza sovrascrivere nulla)
    json_file = open('json1.dbt', 'a',encoding='utf-8')

    # Le variabili nCabina, nPonte, temp, umid e TS
    # verranno definite nella fase di acquisizione dati

    # FASE 2: acquisizione dati da server (socket)
    # 

    # Costruzione formato JSON
    # Dizionario
    Dati = {"Cabina": nCabina,"Ponte": nPonte, "Rilevazione": nRilevazione,"Data e ora": TS,
       "Temperatura": temp, "Umidità": umid}
    
    # Scrittura di un singolo oggetto JSON per ogni rilevazione
    # in modalità append sul file
    json.dump(Dati, json_file, indent=4)    
                                      
    print ("-----------------------------")
    print ("Documento JSON salvato su file")
    print ("-----------------------------")

    # Chiusura del file json
    json_file.close()
    nRilevazione += 1

