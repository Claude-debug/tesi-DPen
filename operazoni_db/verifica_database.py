import sqlite3

# Verifica il contenuto del database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

print("Tabella users:")
for row in cursor.execute("SELECT * FROM users"):
    print(row)

print("\nTabella pazienti:")
for row in cursor.execute("SELECT * FROM pazienti"):
    print(row)

print("\nTabella iniezioni:")
for row in cursor.execute("SELECT * FROM iniezioni"):
    print(row)

conn.close()
