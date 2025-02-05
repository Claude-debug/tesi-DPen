import sqlite3

# Aggiungi medici al database
def aggiungi_medico(nome, cognome, email, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO users (nome, cognome, email, password, ruolo)
        VALUES (?, ?, ?, ?, 'medico')
        """, (nome, cognome, email, password))
        conn.commit()
        print(f"Medico {nome} {cognome} aggiunto con successo!")
    except sqlite3.IntegrityError:
        print("Errore: L'email esiste già!")
    finally:
        conn.close()

# Inserisci i medici
aggiungi_medico("Mario", "Rossi", "mario.rossi@example.com", "password123")
aggiungi_medico("Anna", "Verdi", "anna.verdi@example.com", "password456")
