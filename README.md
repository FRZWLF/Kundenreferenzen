# Kundenreferenzen

Ausgabe von Intershop-Kundenreferenzen und Empfehlung von Intershop-Produkten, basierend auf spezifische Herausforderungen.
Dieses Projekt umfasst **Daten-Scraping**, **semantische Analyse** und eine **benutzerfreundliche Oberfläche** für interaktive Filterung und Visualisierung.

---

## **Features**

- **Scraping**:
  - Automatisches Laden von Kundendaten und -herausforderungen sowie Produktdaten von der Intershop-Website.
  - Möglichkeit, bestehende Daten direkt über die Oberfläche zu aktualisieren (Rescraping).

- **Semantische Analyse**:
  - Automatische Kategorisierung von Herausforderungen durch Sentence Transformers.
  - Empfehlungssystem für Kundenreferenzen und Produkten basierend auf Kosinus-Ähnlichkeit.

- **Visualisierung**:
  - Diagramm stellt die Kategorien und Anzahl der entsprechenden Kundenreferenzen dar.
  - Herausforderungen wurden mit semantischer Analyse entsprechenden Kategorien zugeordnet.

- **Benutzerfreundlichkeit**:
  - Interaktive Filterung nach Kategorien und Ähnlichkeit.
  - Erfolgsmeldung und Ladeanimation bei Rescraping.

---

## Anforderungen
- **Python-Version**: Python 3.12
- **Anaconda**
- **Datenbank**: MongoDB Community Server [Download MongoDB](https://www.mongodb.com/try/download/community)

  - **Wichtig:** MongoDB braucht einen **data-Ordner**. Erstelle einen Ordner an der Stelle, wo MongoDB Dateien gespeichert werden sollen.

---

## Setup-Schritte

1. **Repository klonen:**
```bash
git clone https://github.com/FRZWLF/Kundenreferenzen.git
cd Kundenreferenzen
```
2. **Conda-Umgebung erstellen:**
```bash
conda create --name myenv python=3.12
conda activate myenv
```
3. **Requirements installieren:**
```bash
pip install -r requirements.txt
```
4. **Lokalen MongoDB-Server starten:**
- Unter Windows:
  - Öffne ein Terminal oder die Eingabeaufforderung.
  - Navigiere zum MongoDB-Installations-Pfad (z.b.: /path/to/mongodb/bin)
  - Führe den folgenden Befehl aus (ersetze /path/to/data/directory durch deinen Data-Ordner):
```bash
./mongod --dbpath=/path/to/data/directory
```
MongoDB läuft standardmäßig unter: mongodb://localhost:27017/
5. **Flask-Anwendung starten:**
```bash
python main.py
```
Die Anwendung wird unter http://127.0.0.1:5000 erreichbar sein.

___

## TO-DO
- **Suche und Empfehlung verbessern** (z.b. durch besser aufbereitete Ausgangsdaten)
- **Oberfläche anpassen:** Weitere Details und zusätzliche Interaktionsmöglichkeiten integrieren.
- **Variablen und Bezeichner vereinheitlichen:** Variablennamen und Bezeichner im Frontend und Backend an entsprechende Vorgaben anpassen
- **Frontend:** Erstellung von Variablen und Klassen für wiederholenden CSS-Code
