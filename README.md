# 🖊 di-Pen App - Gestione Somministrazioni Insulina

**di-Pen App** è un'applicazione sviluppata in **Python con Kivy**, progettata per gestire la somministrazione di insulina tramite **di-Pen**, un cappuccio smart low-budget in grado di registrare e processare con AI automaticamente le somministrazioni di insulina, rendendo la penna insulinica smart.  
L'app consente a **pazienti e medici** di monitorare le iniezioni e raccogliere dati in un **database SQLite**, offrendo una gestione efficiente e sicura delle somministrazioni.

## 👥 Sviluppatore
**Claudio Dragotta** - Sviluppatore principale  


## 🛠 Funzionalità Attualmente Implementate
✅ **Login per pazienti, medici e superutenti**  
✅ **Gestione della registrazione di nuovi utenti**  
✅ **Salvataggio delle iniezioni nel database SQLite**  
✅ **Visualizzazione dello storico delle iniezioni per pazienti e medici**  
✅ **Generazione e scansione di QR Code** per confermare la somministrazione  
✅ **Avvisi automatici** per suggerire il cambio del punto di iniezione**  
✅ **Possibilità per i superutenti** di modificare le password degli utenti  

## 🚀 Tecnologie Utilizzate
- **Python 3.9.13** - Linguaggio di programmazione principale  
- **Kivy** - Framework per lo sviluppo dell'interfaccia grafica  
- **SQLite** - Database locale per la gestione degli utenti e delle iniezioni  

## ⚙️ Installazione e Avvio

Per installare e avviare l'applicazione, segui questi passaggi:  

1. Clonare il repository GitHub con il comando:  
   ```bash
   git clone https://github.com/NomeUtente/di-Pen-App.git
   cd di-Pen-App

2. Installazione ambiente virtuale attraverso il terminale:
    ```bash
    python -m venv venv


3. Attivazione ambianete virtuale:
    ```bash
    venv\Scripts\activate

4. Installazione delle dipendenze necessarie con:
    ```bash
    pip install -r requirements.txt

5. Avviare l'applicazione con il comando:
    ```bash
    python main.py
