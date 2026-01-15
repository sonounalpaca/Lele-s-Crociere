"""
misurazione.py simula il funzionamento di un sensore 
generando valori casuali di temperatura e umidità
"""
    
import random

def get_temperature(min_temp, max_temp, n_decimali):
    """
    Simulazione sensore temperatura. 
    Funzione che genera un valore di temperatura casuale da min a max gradi
    con cifre decimali pari a N
    """
    temperatura = random.uniform(min_temp, max_temp) #genera un numero casuale tra due valori
    return round(temperatura, n_decimali) #round limita il numero di decimali


def get_humidity(min_hum, max_hum, n_decimali):
    """
    Simulazione sensore umidità. 
    Funzione che genera un valore di umidità casuale da min a max percentuale di umidità
    con cifre decimali pari a N
    """
    umidita = random.uniform(min_hum, max_hum)
    return round(umidita, n_decimali)

