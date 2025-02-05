import sqlite3

def visualizza_pazienti():
    try:
        # Connessione al database
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Query per ottenere i dettagli dei pazienti
        query = """
        SELECT 
            p.id AS paziente_id,
            u.nome AS paziente_nome,
            u.cognome AS paziente_cognome,
            m.nome AS medico_nome,
            m.cognome AS medico_cognome
        FROM 
            pazienti p
        JOIN 
            users u ON p.id = u.id
        JOIN 
            users m ON p.medico_id = m.id
        ORDER BY 
            u.cognome, u.nome;
        """
        cursor.execute(query)
        risultati = cursor.fetchall()

        # Stampa i risultati
        print("Lista dei pazienti:")
        if risultati:
            for paziente in risultati:
                paziente_id, paziente_nome, paziente_cognome, medico_nome, medico_cognome = paziente
                print(f"ID: {paziente_id}, Nome: {paziente_nome}, Cognome: {paziente_cognome}, Medico: {medico_nome} {medico_cognome}")
        else:
            print("Nessun paziente trovato nel database.")

    except sqlite3.Error as e:
        print(f"Errore durante la connessione al database: {e}")
    finally:
        conn.close()

# Esegui la funzione
if __name__ == "__main__":
    visualizza_pazienti()
