import sqlite3

def lista_utenti():
    """
    Restituisce una lista di tuple (id, nome, cognome, ruolo) per tutti gli utenti
    presenti nella tabella 'users'.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cognome, ruolo FROM users ORDER BY id")
    utenti = cursor.fetchall()
    conn.close()
    return utenti

def elimina_utente(utente_id):
    """
    Elimina l'utente con id 'utente_id' dalla tabella 'users'. Se l'utente ha ruolo
    'paziente', elimina anche il record corrispondente nella tabella 'pazienti'.
    
    Restituisce True se l'eliminazione ha avuto successo, altrimenti False.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Verifica che l'utente esista e recupera il suo ruolo
    cursor.execute("SELECT ruolo FROM users WHERE id = ?", (utente_id,))
    result = cursor.fetchone()
    if not result:
        print("Utente non trovato.")
        conn.close()
        return False
    ruolo = result[0]
    
    # Se l'utente è un paziente, elimina anche il record in 'pazienti'
    if ruolo.lower() == "paziente":
        cursor.execute("DELETE FROM pazienti WHERE id = ?", (utente_id,))
    
    # Elimina l'utente dalla tabella 'users'
    cursor.execute("DELETE FROM users WHERE id = ?", (utente_id,))
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    utenti = lista_utenti()
    
    if not utenti:
        print("Non ci sono utenti nel database.")
        exit(0)
    
    print("Elenco degli utenti:")
    for utente in utenti:
        # Ogni tupla ha il formato: (id, nome, cognome, ruolo)
        print(f"ID: {utente[0]} - {utente[1]} {utente[2]} ({utente[3]})")
    
    try:
        selected_id = int(input("\nInserisci l'ID dell'utente da eliminare: "))
    except ValueError:
        print("ID non valido. Inserisci un numero intero.")
        exit(1)
    
    conferma = input(f"Sei sicuro di voler eliminare l'utente con ID {selected_id}? (s/n): ")
    if conferma.lower() == 's':
        if elimina_utente(selected_id):
            print(f"Utente con ID {selected_id} eliminato con successo.")
        else:
            print("Eliminazione fallita.")
    else:
        print("Eliminazione annullata.")
