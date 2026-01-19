"""
misurazione.py simula il funzionamento di un sensore 
generando valori casuali di temperatura e umidità
"""
    
import random #libreria per la geneerazione dei numeri casuali

def on_temperatura(N):
    """
    Simulazione sensore temperatura. 
    Funzione che genera un valore di temperatura casuale da min a max gradi
    con cifre decimali pari a N
    """
    TEMP = round(random.uniform(10,40), N) #round limita il numero di decimali e uniform genera un numero casuale tra due valori
    return TEMP

def on_umidita(N):
    """
    Simulazione sensore umidità. 
    Funzione che genera un valore di umidità casuale da min a max percentuale di umidità
    con cifre decimali pari a N
    """
    UMID = round(random.uniform(20,90), N)
    return UMID
