import sqlite3

# Funzione per aggiungere un nuovo medico
def aggiungi_medico(nome, cognome, email, password):
    conn = sqlite3.connect("users.db")  # Collega il database
    cursor = conn.cursor()

    try:
        # Inserisce il medico nella tabella users
        cursor.execute("""
        INSERT INTO users (nome, cognome, email, password, ruolo)
        VALUES (?, ?, ?, ?, 'medico')
        """, (nome, cognome, email, password))
        conn.commit()
        print(f"Medico {nome} {cognome} aggiunto con successo!")
    except sqlite3.IntegrityError:
        print("Errore: L'email esiste già nel database!")
    finally:
        conn.close()

# Richiedi i dati al terminale
nome = input("Inserisci il nome del medico: ")
cognome = input("Inserisci il cognome del medico: ")
email = input("Inserisci l'email del medico: ")
password = input("Inserisci la password del medico: ")

# Aggiungi il medico
aggiungi_medico(nome, cognome, email, password)
