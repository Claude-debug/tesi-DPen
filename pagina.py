import sqlite3
import datetime

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

# Carichiamo i file KV (assicurati di non duplicare la definizione di screen)
Builder.load_file("login.kv")
Builder.load_file("home.kv")
Builder.load_file("detail.kv")
Builder.load_file("changepassword.kv")
Builder.load_file("newinjection.kv")


# --- Funzioni utili ---

def verify_credentials(email, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, ruolo, nome FROM users WHERE email=? AND password=?", (email, password))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"id": result[0], "ruolo": result[1], "nome": result[2]}
    return None


# --- Screen Definitions ---

class LoginScreen(Screen):
    def do_login(self):
        email = self.ids.email_input.text
        password = self.ids.password_input.text
        user = verify_credentials(email, password)
        if user:
            self.manager.current_user = user
            self.manager.current = "home"
        else:
            self.ids.error_label.text = "Credenziali errate!"


class HomeScreen(Screen):
    def on_enter(self):
        # Aggiorna l'header con il nome dell'utente
        self.ids.header_label.text = f"Benvenuto, {self.manager.current_user['nome']}"
        self.load_content()

    def load_content(self):
        role = self.manager.current_user["ruolo"]
        container = self.ids.content_container
        container.clear_widgets()

        if role == "paziente":
            self.load_patient_content(container)
        elif role == "medico":
            self.load_doctor_content(container)
        elif role == "superutente":
            self.load_superuser_content(container)

    def load_patient_content(self, container):
        # Query per ottenere le iniezioni del paziente
        user_id = self.manager.current_user["id"]
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT data, ora, quantita, punto FROM iniezioni WHERE paziente_id=? ORDER BY data, ora", (user_id,))
        records = cursor.fetchall()
        conn.close()

        # Creiamo una tabella con 4 colonne
        table = GridLayout(cols=4, spacing=5, size_hint_y=None)
        table.bind(minimum_height=table.setter('height'))
        # Intestazione
        table.add_widget(Label(text="[b]Data[/b]", markup=True))
        table.add_widget(Label(text="[b]Ora[/b]", markup=True))
        table.add_widget(Label(text="[b]Quantità[/b]", markup=True))
        table.add_widget(Label(text="[b]Punto[/b]", markup=True))
        # Dati
        for rec in records:
            for field in rec:
                table.add_widget(Label(text=str(field)))
        container.add_widget(table)

    def load_doctor_content(self, container):
        # Query per ottenere i pazienti associati al medico
        doctor_id = self.manager.current_user["id"]
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.nome, u.cognome, COUNT(i.id)
            FROM pazienti p
            JOIN users u ON p.id = u.id
            LEFT JOIN iniezioni i ON i.paziente_id = u.id
            WHERE p.medico_id=?
            GROUP BY u.id
        """, (doctor_id,))
        records = cursor.fetchall()
        conn.close()

        table = GridLayout(cols=3, spacing=5, size_hint_y=None)
        table.bind(minimum_height=table.setter('height'))
        # Intestazione
        table.add_widget(Label(text="[b]Nome[/b]", markup=True))
        table.add_widget(Label(text="[b]Cognome[/b]", markup=True))
        table.add_widget(Label(text="[b]Iniezioni[/b]", markup=True))
        # Dati: per ogni paziente, il pulsante per vedere i dettagli
        for rec in records:
            patient_id, nome, cognome, total = rec
            table.add_widget(Label(text=nome))
            table.add_widget(Label(text=cognome))
            btn = Button(text=str(total))
            btn.bind(on_release=lambda instance, pid=patient_id: self.show_patient_detail(pid))
            table.add_widget(btn)
        container.add_widget(table)

    def load_superuser_content(self, container):
        # Per il superutente, due tabelle: Medici e Pazienti
        box = BoxLayout(orientation="vertical", spacing=10)
        # Tabella Medici
        label_medics = Label(text="[b]Medici[/b]", markup=True, size_hint_y=None, height="30dp")
        box.add_widget(label_medics)
        table_medics = GridLayout(cols=3, spacing=5, size_hint_y=None)
        table_medics.bind(minimum_height=table_medics.setter('height'))
        table_medics.add_widget(Label(text="[b]Nome[/b]", markup=True))
        table_medics.add_widget(Label(text="[b]Cognome[/b]", markup=True))
        table_medics.add_widget(Label(text="[b]Azioni[/b]", markup=True))
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cognome FROM users WHERE ruolo='medico'")
        medics = cursor.fetchall()
        conn.close()
        for med in medics:
            med_id, nome, cognome = med
            table_medics.add_widget(Label(text=nome))
            table_medics.add_widget(Label(text=cognome))
            btn = Button(text="Vedi Pazienti")
            btn.bind(on_release=lambda instance, mid=med_id: self.show_patients_of_medic(mid))
            table_medics.add_widget(btn)
        box.add_widget(table_medics)

        # Tabella Pazienti
        label_patients = Label(text="[b]Pazienti[/b]", markup=True, size_hint_y=None, height="30dp")
        box.add_widget(label_patients)
        table_patients = GridLayout(cols=3, spacing=5, size_hint_y=None)
        table_patients.bind(minimum_height=table_patients.setter('height'))
        table_patients.add_widget(Label(text="[b]Nome[/b]", markup=True))
        table_patients.add_widget(Label(text="[b]Cognome[/b]", markup=True))
        table_patients.add_widget(Label(text="[b]Iniezioni[/b]", markup=True))
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT u.id, u.nome, u.cognome FROM pazienti p JOIN users u ON p.id = u.id")
        patients = cursor.fetchall()
        conn.close()
        for pat in patients:
            pat_id, nome, cognome = pat
            table_patients.add_widget(Label(text=nome))
            table_patients.add_widget(Label(text=cognome))
            btn = Button(text="Vedi Iniezioni")
            btn.bind(on_release=lambda instance, pid=pat_id: self.show_patient_detail(pid))
            table_patients.add_widget(btn)
        box.add_widget(table_patients)
        container.add_widget(box)

    def show_patient_detail(self, patient_id):
        self.manager.paziente_selezionato = patient_id
        self.manager.current = "detail"

    def show_patients_of_medic(self, medic_id):
        self.manager.medico_selezionato = medic_id
        self.manager.current = "detail"


class DetailScreen(Screen):
    def on_enter(self):
        # In base alla selezione, mostriamo il dettaglio delle iniezioni o dei pazienti di un medico
        if self.manager.paziente_selezionato:
            self.load_injections(self.manager.paziente_selezionato)
        elif self.manager.medico_selezionato:
            self.load_patients_of_medic(self.manager.medico_selezionato)

    def load_injections(self, patient_id):
        container = self.ids.detail_container
        container.clear_widgets()
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT data, ora, quantita, punto FROM iniezioni WHERE paziente_id=? ORDER BY data, ora", (patient_id,))
        records = cursor.fetchall()
        conn.close()

        table = GridLayout(cols=4, spacing=5, size_hint_y=None)
        table.bind(minimum_height=table.setter('height'))
        table.add_widget(Label(text="[b]Data[/b]", markup=True))
        table.add_widget(Label(text="[b]Ora[/b]", markup=True))
        table.add_widget(Label(text="[b]Quantità[/b]", markup=True))
        table.add_widget(Label(text="[b]Punto[/b]", markup=True))
        for rec in records:
            for field in rec:
                table.add_widget(Label(text=str(field)))
        container.add_widget(table)

    def load_patients_of_medic(self, medic_id):
        container = self.ids.detail_container
        container.clear_widgets()
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.nome, u.cognome, COUNT(i.id)
            FROM pazienti p
            JOIN users u ON p.id = u.id
            LEFT JOIN iniezioni i ON i.paziente_id = u.id
            WHERE p.medico_id=?
            GROUP BY u.id
        """, (medic_id,))
        records = cursor.fetchall()
        conn.close()

        table = GridLayout(cols=3, spacing=5, size_hint_y=None)
        table.bind(minimum_height=table.setter('height'))
        table.add_widget(Label(text="[b]Nome[/b]", markup=True))
        table.add_widget(Label(text="[b]Cognome[/b]", markup=True))
        table.add_widget(Label(text="[b]Iniezioni[/b]", markup=True))
        for rec in records:
            patient_id, nome, cognome, total = rec
            table.add_widget(Label(text=nome))
            table.add_widget(Label(text=cognome))
            btn = Button(text=str(total))
            btn.bind(on_release=lambda instance, pid=patient_id: self.manager.current = "detail")
            table.add_widget(btn)
        container.add_widget(table)


class ChangePasswordScreen(Screen):
    def change_password(self):
        # Logica per il cambio password (per superutente)
        new_pass = self.ids.new_password.text
        # Aggiorna il database...
        self.ids.info_label.text = "Password cambiata!"


class NewInjectionScreen(Screen):
    def register_injection(self):
        # Logica per registrare una nuova iniezione per il paziente
        pass


class MyScreenManager(ScreenManager):
    current_user = ObjectProperty({"nome": "", "ruolo": ""})
    paziente_selezionato = ObjectProperty(None)
    medico_selezionato = ObjectProperty(None)


class MyApp(App):
    def build(self):
        sm = MyScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(DetailScreen(name="detail"))
        sm.add_widget(ChangePasswordScreen(name="changepassword"))
        sm.add_widget(NewInjectionScreen(name="newinjection"))
        return sm


if __name__ == "__main__":
    MyApp().run()
