import sqlite3

def lista_pazienti():
    """
    Restituisce una lista di tuple (id, nome, cognome) per tutti i pazienti nel database.
    I pazienti sono identificati nel database dalla colonna 'ruolo' con valore 'paziente'.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cognome FROM users WHERE ruolo = 'paziente'")
    pazienti = cursor.fetchall()
    conn.close()
    return pazienti

def get_iniezioni_per_paziente(paziente_id):
    """
    Restituisce una lista di tuple contenenti i dati delle iniezioni associate al paziente con ID 'paziente_id'.
    Ogni tupla contiene: (data, ora, quantita, punto)
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = """
        SELECT data, ora, quantita, punto
        FROM iniezioni
        WHERE paziente_id = ?
        ORDER BY data, ora
    """
    cursor.execute(query, (paziente_id,))
    iniezioni = cursor.fetchall()
    conn.close()
    return iniezioni

if __name__ == "__main__":
    # Elenca tutti i pazienti
    pazienti = lista_pazienti()
    
    if not pazienti:
        print("Non ci sono pazienti nel database.")
        exit(0)
    
    print("Elenco dei pazienti:")
    for paziente in pazienti:
        print(f"ID: {paziente[0]} - {paziente[1]} {paziente[2]}")
    
    try:
        selected_id = int(input("\nInserisci l'ID del paziente per visualizzare le sue iniezioni: "))
    except ValueError:
        print("ID non valido. Inserisci un numero intero.")
        exit(1)
    
    iniezioni = get_iniezioni_per_paziente(selected_id)
    
    if iniezioni:
        print(f"\nIniezioni per il paziente con ID {selected_id}:")
        for data, ora, quantita, punto in iniezioni:
            print(f"Data: {data}, Ora: {ora}, Quantità: {quantita} U/ml, Punto: {punto}")
    else:
        print(f"\nNessuna iniezione trovata per il paziente con ID {selected_id}.")
