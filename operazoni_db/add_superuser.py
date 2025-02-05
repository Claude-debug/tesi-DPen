import sqlite3

# Connetti al database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Aggiungi il superutente
try:
    cursor.execute("""
        INSERT INTO users (nome, cognome, email, password, ruolo)
        VALUES (?, ?, ?, ?, ?)
    """, ("Super", "User", "superutente@example.com", "password123", "superutente"))
    conn.commit()
    print("Superutente aggiunto con successo!")
except sqlite3.IntegrityError:
    print("Errore: L'email esiste già!")
finally:
    conn.close()
