import sqlite3

# Crea il database users.db
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Crea la tabella users
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cognome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    ruolo TEXT NOT NULL -- "medico" o "paziente"
)
""")

# Crea la tabella pazienti
cursor.execute("""
CREATE TABLE IF NOT EXISTS pazienti (
    id INTEGER PRIMARY KEY,
    medico_id INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES users (id),
    FOREIGN KEY (medico_id) REFERENCES users (id)
)
""")

# Crea la tabella iniezioni
cursor.execute("""
CREATE TABLE IF NOT EXISTS iniezioni (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paziente_id INTEGER NOT NULL,
    data TEXT NOT NULL,
    ora TEXT NOT NULL,
    punto TEXT NOT NULL,
    quantita REAL NOT NULL,
    FOREIGN KEY (paziente_id) REFERENCES pazienti (id)
)
""")

conn.commit()
conn.close()
print("Database creato con successo!")
