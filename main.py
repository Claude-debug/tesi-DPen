import sqlite3
import random
import datetime
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import StringProperty, BooleanProperty
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime

# Carica i file KV
Builder.load_file("login.kv")
Builder.load_file("pagina_home.kv")
Builder.load_file("nuova_iniezione.kv")
Builder.load_file("cambia_password.kv")
Builder.load_file("schermata_iniezioni_paziente.kv")
# Funzione per verificare le credenziali
def verifica_credenziali(email, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, ruolo, nome FROM users WHERE email = ? AND password = ?", (email, password))
    risultato = cursor.fetchone()
    conn.close()

    if risultato:
        return {"id": risultato[0], "ruolo": risultato[1], "nome": risultato[2]}
    return None

# Funzione per verificare se un'email esiste nel database
def verifica_email(email):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    risultato = cursor.fetchone()
    conn.close()

    return risultato is not None

# Schermata di Login
class LoginScreen(Screen):

    def effettua_login(self):
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not email or not password:
            self.ids.error_label.text = "Inserisci sia l'email che la password."
            self.ids.error_label.color = (1, 0, 0, 1) 
            return

        utente = verifica_credenziali(email, password)

        if utente:
            self.manager.current_user = utente
            if utente["ruolo"] == "medico":
                print("Accesso come medico")  # Log per il debug
                self.manager.current = "pagina_home"
            elif utente["ruolo"] == "paziente":
                print("Accesso come paziente")  # Log per il debug
                self.manager.current = "pagina_home"
            elif utente["ruolo"] == "superutente":
                print("Accesso come superutente")  # Log per il debug
                self.manager.current = "pagina_home"
        else:
            #se le credenziali sono errate
            self.ids.error_label.text =  "Email o password errate."
            self.ids.error_label.color = (1, 0, 0, 1) 

# Schermata per Password Dimenticata
class PasswordDimenticataScreen(Screen):
    def reset_password(self):
        email = self.ids.email_input.text

        if verifica_email(email):
            self.ids.message_label.text = "Email inviata! Controlla la tua casella di posta."
            self.ids.message_label.color = (0, 1, 0, 1)
        else:
            self.ids.message_label.text = "Errore: Email non trovata."
            self.ids.message_label.color = (1, 0, 0, 1)

# Schermata di Registrazione
class RegistrazioneScreen(Screen):
    def on_enter(self):
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cognome FROM users WHERE ruolo = 'medico'")
        medici = cursor.fetchall()
        conn.close()
        self.ids.medico_spinner.values = [f"{m[1]} {m[2]}" for m in medici]

    def registra_utente(self):
        nome = self.ids.nome_input.text.strip()
        cognome = self.ids.cognome_input.text.strip()
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()
        medico_selezionato = self.ids.medico_spinner.text

        if not nome or not cognome or not email or not password:
            self.ids.error_label.text = "Tutti i campi sono obbligatori."
            return

        if medico_selezionato == "Seleziona un medico":
            self.ids.error_label.text = "Seleziona un medico valido."
            return

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE ruolo = 'medico' AND nome || ' ' || cognome = ?", (medico_selezionato,))
        medico_id = cursor.fetchone()

        if not medico_id:
            self.ids.error_label.text = "Errore nella selezione del medico."
            conn.close()
            return

        medico_id = medico_id[0]

        try:
            cursor.execute("""
            INSERT INTO users (nome, cognome, email, password, ruolo)
            VALUES (?, ?, ?, ?, 'paziente')
            """, (nome, cognome, email, password))
            conn.commit()

            paziente_id = cursor.lastrowid
            cursor.execute("""
            INSERT INTO pazienti (id, medico_id)
            VALUES (?, ?)
            """, (paziente_id, medico_id))
            conn.commit()

            self.ids.error_label.color = (0, 1, 0, 1)
            self.ids.error_label.text = "Registrazione completata!"
            self.manager.current = "login"

        except sqlite3.IntegrityError:
            self.ids.error_label.text = "Errore: L'email esiste già."
        finally:
            conn.close()

class CambiaPasswordScreen(Screen):
    utente_selezionato = StringProperty("")

    def on_enter(self):
        """Controlla il ruolo e carica gli utenti se è un superutente"""
        utente = self.manager.current_user

        if utente["ruolo"] != "superutente":
            self.manager.current = "pagina_home"  # Se non è superutente, torna alla home
            return

        self.carica_utenti()

    def carica_utenti(self):
        """Recupera gli utenti dal database e aggiorna lo Spinner"""
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cognome FROM users")
        utenti = [f"{row[1]} {row[2]}" for row in cursor.fetchall()]  # Nome + Cognome
        conn.close()

        if utenti:
            self.ids.spinner_utenti.values = utenti
        else:
            self.ids.spinner_utenti.text = "Nessun utente trovato"

    def seleziona_utente(self, nome_completo):
        """Memorizza l'ID dell'utente selezionato"""
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Dividere Nome e Cognome (gestisce anche nomi composti)
        nome_cognome = nome_completo.split(" ", 1)
        if len(nome_cognome) < 2:
            return  # Se manca il cognome, non fare nulla

        nome, cognome = nome_cognome

        cursor.execute("SELECT id FROM users WHERE nome = ? AND cognome = ?", (nome, cognome))
        result = cursor.fetchone()
        conn.close()

        if result:
            self.utente_selezionato = str(result[0])  # Convertiamo l'ID in STRINGA
        else:
            self.utente_selezionato = ""

    def cambia_password(self):
        """Cambia la password dell'utente selezionato"""
        nuova_password = self.ids.nuova_password.text.strip()

        if not self.utente_selezionato:
            self.mostra_popup("Errore", "Seleziona un utente!")
            return

        if not nuova_password:
            self.mostra_popup("Errore", "Inserisci una nuova password!")
            return

        print(f"DEBUG: Cambiando password per utente ID {self.utente_selezionato}")

        # Aggiorna la password nel database
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (nuova_password, self.utente_selezionato))
            conn.commit()
            print("DEBUG: Password aggiornata con successo nel database")
        except sqlite3.Error as e:
            print(f"Errore SQLite: {e}")
            self.mostra_popup("Errore", "Errore durante l'aggiornamento della password")
        finally:
            conn.close()

        self.mostra_popup("Successo", "Password aggiornata con successo!")
        self.ids.nuova_password.text = ""  # Reset del campo password

    def mostra_popup(self, titolo, messaggio):
        """Mostra un popup di conferma o errore"""
        popup_content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        popup_content.add_widget(Label(text=messaggio))

        btn_ok = Button(text="OK", size_hint_y=None, height="40dp")
        popup_content.add_widget(btn_ok)

        popup = Popup(title=titolo, content=popup_content, size_hint=(None, None), size=(300, 200))
        btn_ok.bind(on_release=popup.dismiss)
        popup.open()

# Schermata Home (Dinamica per Pazienti/Medici/Superutente)
class PaginaHome(Screen):
    search_text = StringProperty("")
    popup = ObjectProperty(None)
    

    def on_enter(self):
        utente = self.manager.current_user
        #self.ids.user_label.text = f"Benvenuto, {utente['nome']} ({utente['ruolo']})"
        self.carica_contenuto()

      # Verifica che il contenitore dei pulsanti esista
        btn_nuova_iniezione = self.ids.get("btn_nuova_iniezione")
        btn_cambia_password = self.ids.get("btn_cambia_password")

        # Rimozione sicura dal container dei pulsanti:
        if btn_nuova_iniezione is not None:
            try:
                if btn_nuova_iniezione in list(self.ids.btn_container.children):
                    self.ids.btn_container.remove_widget(btn_nuova_iniezione)
            except ReferenceError:
                pass

        if btn_cambia_password is not None:
            try:
                if btn_cambia_password in list(self.ids.btn_container.children):
                    self.ids.btn_container.remove_widget(btn_cambia_password)
            except ReferenceError:
                pass

        # Aggiungi i pulsanti in base al ruolo:
        if utente["ruolo"] == "paziente":
            if btn_nuova_iniezione is not None and btn_nuova_iniezione not in self.ids.btn_container.children:
                self.ids.btn_container.add_widget(btn_nuova_iniezione)
        elif utente["ruolo"] == "superutente":
            if btn_cambia_password is not None and btn_cambia_password not in self.ids.btn_container.children:
                self.ids.btn_container.add_widget(btn_cambia_password)
    
    def carica_contenuto(self):
        """Carica il contenuto dinamico in base al ruolo dell'utente."""
        ruolo = self.manager.current_user["ruolo"]
        contenitore = self.ids.content_container
        contenitore.clear_widgets()

        if ruolo == "paziente":
            self.mostra_iniezioni_paziente(contenitore)
        elif ruolo == "medico":
            self.mostra_pazienti_medico(contenitore)
        elif ruolo == "superutente":
            self.mostra_medici(contenitore)
            self.mostra_pazienti_superutente(contenitore)
                 
    def aggiorna_lista_iniezioni(self, records):
        """Mostra l'elenco delle iniezioni."""
        container = self.ids.patients_container
        container.clear_widgets()

        if records:
            for data, ora, quantita, punto in records:
                container.add_widget(Label(text=str(data), size_hint_y=None, height="40dp"))
                container.add_widget(Label(text=str(ora), size_hint_y=None, height="40dp"))
                container.add_widget(Label(text=str(quantita), size_hint_y=None, height="40dp"))
                container.add_widget(Label(text=str(punto), size_hint_y=None, height="40dp"))
        else:
            container.add_widget(Label(text="Nessuna iniezione trovata.", size_hint_y=None, height="40dp")) 

    def on_search(self, text):
        # Logica per cercare tra i dati
        self.search_text = text.lower()  # Per filtrare o evidenziare i risultati
        print(f"Searching for: {self.search_text}")
   
    def clear_search(self):
        """Cancella il testo della ricerca e ripristina la lista completa."""
        self.ids.search_input.text = ""
        self.carica_iniezioni()

    def logout(self):
        """Gestisce il logout e resetta la sessione"""
        print("Logout in esecuzione...")

        # Imposta un utente vuoto invece di None
        self.manager.current_user = {"nome": "", "ruolo": ""}

        # Torna alla schermata di login
        self.manager.current = "login"

        # Pulisce i campi di input della login (se esistono)
        if "input_email" in self.ids:
            self.ids.input_email.text = ""
        if "input_password" in self.ids:
            self.ids.input_password.text = ""

        print("Transizione a login completata!")

    def open_menu(self, widget):
        """Apre un menu popup sotto il widget cliccato."""
        if self.popup:
            self.popup.dismiss()
        utente = self.manager.current_user
        nome = utente["nome"] if utente else "Sconosciuto"

        content = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        content.height = 180 

        btn_info = Button(text=f"Utente: {nome}", size_hint_y=None, height="40dp")
        btn_logout = Button(text="Logout", size_hint_y=None, height="40dp", on_release=lambda x: self.logout())
        btn_close = Button(text="Chiudi", size_hint_y=None, height="40dp", on_release=lambda x: self.popup.dismiss())

        content.add_widget(btn_info)
        content.add_widget(btn_logout)
        content.add_widget(btn_close)

        self.popup = Popup(
            title="Profilo",
            title_align="center",
            title_size="18sp",
            title_color=(1, 1, 1, 1),
            separator_height=0,
            content=content,
            size_hint=(None, None),
            size=(220, 220),
            auto_dismiss=True
        )

        x, y = widget.to_window(widget.x, widget.y)
        self.popup.pos = (x - 80, y - 140)
        self.popup.open()


    def mostra_iniezioni_paziente(self, contenitore):
        """Visualizza per il paziente le proprie iniezioni con un design migliorato."""
        user_id = self.manager.current_user["id"]
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT data, ora, quantita, punto FROM iniezioni WHERE paziente_id = ? ORDER BY data DESC", (user_id,))
        records = cursor.fetchall()
        conn.close()

        # Crea un GridLayout per visualizzare i dati
        table = GridLayout(cols=4, padding=10, spacing=10)
        table.bind(minimum_height=table.setter('height'))

        # Aggiungi l'intestazione con testo evidenziato
        headers = ["Data", "Ora", "Quantità", "Punto"]
        for header in headers:
            label = Label(text=header, font_size="18sp", bold=True, color=(1, 1, 1, 1), size_hint_y=None, height=40)
            table.add_widget(label)

        # Aggiungi i dati delle iniezioni
        for data, ora, quantita, punto in records:
            table.add_widget(Label(text=str(data), font_size="16sp", size_hint_y=None, height=40))
            table.add_widget(Label(text=str(ora), font_size="16sp", size_hint_y=None, height=40))
            table.add_widget(Label(text=f"{quantita} U/ml", font_size="16sp", size_hint_y=None, height=40))
            table.add_widget(Label(text=str(punto), font_size="16sp", size_hint_y=None, height=40))

        contenitore.clear_widgets()
        contenitore.add_widget(table)

    def mostra_pazienti_medico(self, contenitore):
        """
        Visualizza per il medico i pazienti associati
        (Nome, Cognome e Totale Iniezioni). Cliccando su un paziente si
        passa alla schermata di dettaglio per visualizzare le sue iniezioni.
        """
        doctor_id = self.manager.current_user["id"]
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id, u.nome, u.cognome, COUNT(i.id) as totale_iniezioni
            FROM pazienti p
            JOIN users u ON p.id = u.id
            LEFT JOIN iniezioni i ON i.paziente_id = u.id
            WHERE p.medico_id = ?
            GROUP BY u.id
            """,
            (doctor_id,)
        )
        records = cursor.fetchall()
        conn.close()

        table = GridLayout(cols=2, size_hint_y=None, padding=10, spacing=10)
        table.bind(minimum_height=table.setter('height'))

        if records:
            for paziente_id, nome, cognome, totale_iniezioni in records:
                btn = Button(
                    text=f"{nome} {cognome} - {totale_iniezioni} iniezioni",
                    size_hint_y=None,
                    height=40
                )
                btn.bind(on_release=lambda instance, pid=paziente_id: self.mostra_iniezioni_paziente_dettaglio(pid))
                table.add_widget(btn)
        else:
            table.add_widget(Label(text="Nessun paziente associato."))
        contenitore.add_widget(table)

    def mostra_medici(self, contenitore):
        """Visualizza l'elenco dei medici (Nome e Cognome). Cliccando su uno si visualizzano i relativi pazienti."""
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cognome FROM users WHERE ruolo = 'medico'")
        records = cursor.fetchall()
        conn.close()

        table = GridLayout(cols=2, size_hint_y=None)
        table.bind(minimum_height=table.setter('height'))

        if records:
            for medico_id, nome, cognome in records:
                btn = Button(
                    text=f"{nome} {cognome}",
                    size_hint_y=None,
                    height=40
                )
                btn.bind(on_release=lambda instance, mid=medico_id: self.mostra_pazienti_medico_dettaglio(mid))
                table.add_widget(btn)
        else:
            table.add_widget(Label(text="Nessun medico trovato."))
        contenitore.add_widget(table)

    def mostra_pazienti_superutente(self, contenitore):
        """
        Visualizza per il superutente l'elenco di tutti i pazienti
        (Nome, Cognome e Medico associato). Cliccando su un paziente si
        visualizzano le sue iniezioni.
        """
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id, u.nome, u.cognome, m.nome, m.cognome
            FROM pazienti p
            JOIN users u ON p.id = u.id
            JOIN users m ON p.medico_id = m.id
            """
        )
        records = cursor.fetchall()
        conn.close()

        table = GridLayout(cols=2, size_hint_y=None)
        table.bind(minimum_height=table.setter('height'))

        if records:
            for paziente_id, p_nome, p_cognome, m_nome, m_cognome in records:
                btn = Button(
                    text=f"{p_nome} {p_cognome} - Medico: {m_nome} {m_cognome}",
                    size_hint_y=None,
                    height=40
                )
                btn.bind(on_release=lambda instance, pid=paziente_id: self.mostra_iniezioni_paziente_dettaglio(pid))
                table.add_widget(btn)
        else:
            table.add_widget(Label(text="Nessun paziente trovato."))
        contenitore.add_widget(table)

    def mostra_iniezioni_paziente_dettaglio(self, paziente_id):
        """Imposta il paziente selezionato e passa alla schermata di dettaglio per le iniezioni."""
        self.manager.paziente_selezionato = paziente_id
        self.manager.tipo_dettaglio = "iniezioni"
        self.manager.current = "schermata_iniezioni_paziente"

    def mostra_pazienti_medico_dettaglio(self, medico_id):
        """Imposta il medico selezionato e passa alla schermata di dettaglio per visualizzare i pazienti associati."""
        self.manager.medico_selezionato = medico_id
        self.manager.tipo_dettaglio = "pazienti_medico"
        self.manager.current = "schermata_iniezioni_paziente"

class SchermataIniezioniPaziente(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup = None  # Inizializza la variabile popup

    def on_enter(self):
        """Carica i dati in base al tipo di dettaglio richiesto."""
        tipo_dettaglio = self.manager.tipo_dettaglio

        if tipo_dettaglio == "iniezioni":
            self.ids.header_label.text = "Storico Iniezioni"
            self.carica_iniezioni()
        elif tipo_dettaglio == "pazienti_medico":
            self.ids.header_label.text = "Pazienti del Medico"
            self.carica_pazienti_medico()
        elif tipo_dettaglio == "pazienti_superutente":
            self.ids.header_label.text = "Elenco Pazienti"
            self.carica_pazienti_superutente()
        else:
            self.ids.header_label.text = "Dettagli"
            print("Errore: tipo_dettaglio non valido")

    def carica_iniezioni(self):
        """Carica le iniezioni per il paziente selezionato."""
        paziente_id = self.manager.paziente_selezionato
        if not paziente_id:
            self.manager.current = "pagina_home"
            return

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT data, ora, quantita, punto FROM iniezioni WHERE paziente_id = ? ORDER BY data DESC", (paziente_id,))
        records = cursor.fetchall()
        conn.close()

        formatted_records = []
        
        for data, ora, quantita, punto in records:
            try:
                # Prova a interpretare la data nei formati comuni
                if "-" in data:
                    data_format = "%Y-%m-%d"  # Formato SQL classico
                elif "/" in data:
                    data_format = "%d/%m/%Y"  # Formato italiano
                
                parsed_date = datetime.strptime(data, data_format)
                formatted_data = parsed_date.strftime("%d/%m/%Y")  # Converti sempre in formato leggibile

            except ValueError:
                formatted_data = data  # Se non riesce a convertire, usa la data originale

            formatted_records.append((formatted_data, ora, f"{quantita} U/ml", punto))

        self.aggiorna_lista_iniezioni(formatted_records)

    def carica_pazienti_medico(self):
        """Carica i pazienti associati al medico e rende i bottoni cliccabili."""
        medico_id = self.manager.medico_selezionato
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT u.id, u.nome, u.cognome FROM pazienti p JOIN users u ON p.id = u.id WHERE p.medico_id = ?",
            (medico_id,)
        )
        records = cursor.fetchall()
        conn.close()

        self.aggiorna_lista_pazienti(records, "pazienti_medico")

    def crea_callback_mostra_dettagli(self, paziente_id, tipo):
        """Ritorna una funzione che chiama mostra_dettagli_paziente con l'ID corretto."""
        return lambda instance: self.mostra_dettagli_paziente(paziente_id, tipo)

    def carica_pazienti_superutente(self):
        """Carica tutti i pazienti per il superutente."""
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT u.id, u.nome, u.cognome, m.nome, m.cognome FROM pazienti p JOIN users u ON p.id = u.id JOIN users m ON p.medico_id = m.id"
        )
        records = cursor.fetchall()
        conn.close()

        self.aggiorna_lista_pazienti(records, "pazienti_superutente")

    def aggiorna_lista_iniezioni(self, records):
        """Mostra l'elenco delle iniezioni."""
        container = self.ids.detail_container
        container.clear_widgets()

        if records:
            for data, ora, quantita, punto in records:
                container.add_widget(Label(text=str(data), size_hint_y=None, height="40dp"))
                container.add_widget(Label(text=str(ora), size_hint_y=None, height="40dp"))
                container.add_widget(Label(text=str(quantita), size_hint_y=None, height="40dp"))
                container.add_widget(Label(text=str(punto), size_hint_y=None, height="40dp"))
        else:
            container.add_widget(Label(text="Nessuna iniezione trovata.", size_hint_y=None, height="40dp"))

    def mostra_dettagli_paziente(self, paziente_id, tipo):
        """Passa alla schermata dettagliata delle iniezioni del paziente selezionato."""
        self.manager.paziente_selezionato = paziente_id
        self.manager.tipo_dettaglio = "iniezioni"
        self.manager.current = "schermata_iniezioni_paziente"

    def on_search(self, text):
        """Filtra in tempo reale le iniezioni mostrate."""
        search_text = text.lower()
        paziente_id = self.manager.paziente_selezionato
        
        if not paziente_id:
            return

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT data, ora, quantita, punto FROM iniezioni WHERE paziente_id = ? ORDER BY data DESC", (paziente_id,))
        records = cursor.fetchall()
        conn.close()

        # Converti la data e applica il filtro
        formatted_records = [(datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y"), ora, f"{quantita} U/ml", punto) for data, ora, quantita, punto in records]
        
        filtered_records = [record for record in formatted_records if search_text in str(record).lower()]
        self.aggiorna_lista_iniezioni(filtered_records)

    def clear_search(self):
        """Cancella il testo della ricerca e ripristina la lista completa."""
        self.ids.search_input.text = ""
        self.carica_iniezioni()

    def torna_home(self):
        """Torna alla pagina home."""
        self.manager.current = "pagina_home"

    def logout(self):
        """Gestisce il logout e resetta la sessione, poi chiude il popup."""
        print("Logout in esecuzione...")

        # Resetta l'utente
        self.manager.current_user = {"nome": "", "ruolo": ""}

        # Torna alla schermata di login
        self.manager.current = "login"

        # Pulisce i campi di input della login (se esistono)
        if "input_email" in self.ids:
            self.ids.input_email.text = ""
        if "input_password" in self.ids:
            self.ids.input_password.text = ""

        print("Transizione a login completata!")

        # Chiudi il popup dopo il logout
        if self.popup:
            self.popup.dismiss()

    def open_menu(self, widget):
        """Apre un menu popup sotto il widget cliccato."""
        if self.popup:
            self.popup.dismiss()
        
        utente = self.manager.current_user
        nome = utente["nome"] if utente else "Sconosciuto"

        content = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        content.height = 180 

        btn_info = Button(text=f"Utente: {nome}", size_hint_y=None, height="40dp")
        btn_logout = Button(text="Logout", size_hint_y=None, height="40dp", on_release=lambda x: self.logout())
        btn_close = Button(text="Chiudi", size_hint_y=None, height="40dp", on_release=lambda x: self.popup.dismiss())

        content.add_widget(btn_info)
        content.add_widget(btn_logout)
        content.add_widget(btn_close)

        self.popup = Popup(
            title="Profilo",
            title_align="center",
            title_size="18sp",
            title_color=(1, 1, 1, 1),
            separator_height=0,
            content=content,
            size_hint=(None, None),
            size=(220, 220),
            auto_dismiss=True
        )

        x, y = widget.to_window(widget.x, widget.y)
        self.popup.pos = (x - 80, y - 140)
        self.popup.open()

class NuovaIniezioneScreen(Screen):
    data = StringProperty("")
    ora = StringProperty("")
    punto = StringProperty("")
    quantita = StringProperty("1")  # Quantità fissa

    def on_enter(self):
        """Mostra il popup di connessione alla penna all'ingresso della schermata"""
        Clock.schedule_once(lambda dt: self.mostra_popup_connessione(), 0.5)

    def mostra_popup_connessione(self):
        """Popup iniziale per chiedere la connessione alla penna"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Collegare la penna?", font_size="18sp"))

        btn_connetti = Button(text="Connetti", background_color=(0, 1, 0, 1))
        btn_annulla = Button(text="Annulla", background_color=(1, 0, 0, 1))

        btn_connetti.bind(on_release=self.connetti_penna)
        btn_annulla.bind(on_release=lambda x: setattr(self.manager, "current", "pagina_home"))

        content.add_widget(btn_connetti)
        content.add_widget(btn_annulla)

        self.popup = Popup(title="Connessione Penna", content=content, size_hint=(None, None), size=(300, 200))
        self.popup.open()

    def connetti_penna(self, instance):
        """Simula la connessione della penna e riempie automaticamente i dati"""
        self.popup.dismiss()
        self.data = datetime.now().strftime("%d/%m/%Y")
        self.ora = datetime.now().strftime("%H:%M:%S")
        self.punto = random.choice(["Braccio Destro", "Braccio Sinistro", "Coscia Destra", "Coscia Sinistra"])

        # Dopo 5 secondi mostra il popup per salvare i dati
        Clock.schedule_once(lambda dt: self.mostra_popup_salvataggio(), 5)

    def mostra_popup_salvataggio(self):
        """Popup di conferma per salvare il record dopo la connessione"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=f"Data: {self.data}\nOra: {self.ora}\nPunto: {self.punto}\nQuantità: {self.quantita}"))

        btn_salva = Button(text="Salva", background_color=(0, 0.5, 1, 1))
        btn_modifica = Button(text="Modifica", background_color=(1, 0.5, 0, 1))

        btn_salva.bind(on_release=self.salva_record)
        btn_modifica.bind(on_release=self.modifica_dati)

        content.add_widget(btn_salva)
        content.add_widget(btn_modifica)

        self.popup = Popup(title="Salvare il record?", content=content, size_hint=(None, None), size=(350, 300))
        self.popup.open()

    def salva_record(self, instance):
        """Salva il record nel database e verifica l'avviso di cambio punto"""
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO iniezioni (paziente_id, data, ora, punto, quantita)
            VALUES (?, ?, ?, ?, ?)
        """, (self.manager.current_user["id"], self.data, self.ora, self.punto, self.quantita))

        conn.commit()
        conn.close()
        self.popup.dismiss()

        # Controllo se il paziente ha usato lo stesso punto più di 4 volte consecutive
        self.verifica_avviso_punto()

        # Riapre il popup di connessione per una nuova iniezione
        Clock.schedule_once(lambda dt: self.mostra_popup_connessione(), 1)

    def modifica_dati(self, instance):
        """Permette di modificare i dati prima di salvarli"""
        self.popup.dismiss()

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        input_data = TextInput(text=self.data)
        input_ora = TextInput(text=self.ora)
        input_punto = Spinner(text=self.punto, values=["Braccio Destro", "Braccio Sinistro", "Coscia Destra", "Coscia Sinistra"])
        input_quantita = TextInput(text=self.quantita)

        btn_salva = Button(text="Salva", background_color=(0, 0.5, 1, 1))

        content.add_widget(Label(text="Data:"))
        content.add_widget(input_data)
        content.add_widget(Label(text="Ora:"))
        content.add_widget(input_ora)
        content.add_widget(Label(text="Punto:"))
        content.add_widget(input_punto)
        content.add_widget(Label(text="Quantità:"))
        content.add_widget(input_quantita)
        content.add_widget(btn_salva)

        self.popup = Popup(title="Modifica Dati", content=content, size_hint=(None, None), size=(350, 400))
        btn_salva.bind(on_release=lambda x: self.salva_modifiche(input_data, input_ora, input_punto, input_quantita))
        self.popup.open()

    def salva_modifiche(self, input_data, input_ora, input_punto, input_quantita):
        """Salva le modifiche effettuate ai dati prima di salvare nel database"""
        self.data = input_data.text
        self.ora = input_ora.text
        self.punto = input_punto.text
        self.quantita = input_quantita.text
        self.popup.dismiss()
        self.salva_record(None)

    def verifica_avviso_punto(self):
        """Verifica se l'utente ha usato lo stesso punto più di 4 volte consecutive"""
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM iniezioni
            WHERE paziente_id = ? AND punto = ?
            ORDER BY data DESC LIMIT 5
        """, (self.manager.current_user["id"], self.punto))

        count = cursor.fetchone()[0]
        conn.close()

        if count >= 4:
            self.mostra_avviso_cambio_punto()

    def mostra_avviso_cambio_punto(self):
        """Mostra un avviso per suggerire il cambio del punto di iniezione"""
        content = BoxLayout(orientation='vertical', spacing=20, padding=20)

        # Aggiungi la scritta "Attenzione! Cambiare punto di applicazione!" nel popup rosso
        content.add_widget(Label(
            text="Attenzione! Cambiare punto di applicazione!",
            font_size="20sp",
            color=(1, 1, 1, 1),  # Testo bianco
            size_hint_y=None,
            height="40dp",
            halign="center",  # Centra la scritta orizzontalmente
            valign="middle",
        ))

        # Creazione del popup
        self.popup = Popup(
            content=content, 
            size_hint=(None, None), 
            size=(500, 300),  # Una dimensione più piccola per il popup
            background_color=(1, 0, 0, 1),  # Colore rosso di sfondo del popup
            auto_dismiss=True  # Rimuove automaticamente il popup quando clicchi fuori
        )

        # Mostra il popup
        self.popup.open()

    def logout(self):
        """Gestisce il logout e resetta la sessione"""
        print("Logout in esecuzione...")

        # Imposta un utente vuoto invece di None
        self.manager.current_user = {"nome": "", "ruolo": ""}

        # Torna alla schermata di login
        self.manager.current = "login"

        # Pulisce i campi di input della login (se esistono)
        if "input_email" in self.ids:
            self.ids.input_email.text = ""
        if "input_password" in self.ids:
            self.ids.input_password.text = ""

        print("Transizione a login completata!")

    def open_menu(self, widget):
        """Apre un menu popup sotto il widget cliccato."""
        if self.popup:
            self.popup.dismiss()
        utente = self.manager.current_user
        nome = utente["nome"] if utente else "Sconosciuto"

        content = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        content.height = 180 

        btn_info = Button(text=f"Utente: {nome}", size_hint_y=None, height="40dp")
        btn_logout = Button(text="Logout", size_hint_y=None, height="40dp", on_release=lambda x: self.logout())
        btn_close = Button(text="Chiudi", size_hint_y=None, height="40dp", on_release=lambda x: self.popup.dismiss())

        content.add_widget(btn_info)
        content.add_widget(btn_logout)
        content.add_widget(btn_close)

        self.popup = Popup(
            title="Profilo",
            title_align="center",
            title_size="18sp",
            title_color=(1, 1, 1, 1),
            separator_height=0,
            content=content,
            size_hint=(None, None),
            size=(220, 220),
            auto_dismiss=True
        )

        x, y = widget.to_window(widget.x, widget.y)
        self.popup.pos = (x - 80, y - 140)
        self.popup.open()

# Gestore delle schermate
class MyScreenManager(ScreenManager):
    current_user = ObjectProperty({"nome": "", "ruolo": ""})  # Valore predefinito
    tipo_dettaglio = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = {"nome": "", "ruolo": ""}  # Assicura che esista sempre
        self.tipo_dettaglio = ""
    
    selected_patient = ObjectProperty(None)
    selected_doctor = ObjectProperty(None)
    detail_type = StringProperty("")

# Applicazione principale
class MyApp(App):
    def build(self):
        self.title = "Dragotta di-Pen"
        sm = MyScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegistrazioneScreen(name="registrazione"))
        sm.add_widget(PaginaHome(name="pagina_home")) # type: ignore
        sm.add_widget(CambiaPasswordScreen(name="cambia_password"))
        sm.add_widget(NuovaIniezioneScreen(name="nuova_iniezione"))
        sm.add_widget(SchermataIniezioniPaziente(name="schermata_iniezioni_paziente"))

        return sm

if __name__ == "__main__":
    MyApp().run()
