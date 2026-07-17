# Lokaler Offline-Sprachassistent (Wake-Word: "Computer")

Dieses Projekt implementiert einen datenschutzfreundlichen, lokalen Sprachassistenten für Windows. Er hört auf das Aktivierungswort "Computer", antwortet mit einer synthetischen Stimme (TTS), liest Wetterdaten über eine API aus und steuert Nanoleaf-Lichter in deinem lokalen Netzwerk. Komplexe Freitext-Fragen werden vollständig lokal über Ollama verarbeitet.

## Features
- 100% Lokales Speech-to-Text (STT): Nutzt Vosk zur Offline-Spracherkennung.
- Lokales KI-Modell: Verarbeitet allgemeine Fragen über Ollama (gemma4:e2b).
- Wetter-Integration: Aktuelle Vorhersagen und Regenberichte via OpenWeatherMap.
- Smart-Home-Steuerung: Automatische Erkennung und Schaltung von Nanoleaf-Geräten (z. B. Shapes).
- Sprachausgabe (TTS): Antwortet direkt auf Deutsch über die Systemstimme.

---

## Voraussetzungen & Installation

### 1. Windows-Abhängigkeiten (PyAudio)
Da die direkte Installation von PyAudio unter Windows manchmal fehlschlägt, installiere es am besten über pipwin:
```bash
pip install pipwin
pipwin install pyaudio
```


### 2. Python-Bibliotheken installieren

Installiere alle weiteren benötigten Pakete mit folgendem Befehl:

```bash
pip install vosk pyttsx3 requests langchain-core langchain-ollama nanoleafapi zeroconf

```

### 3. Vosk Sprachmodell herunterladen

Für die Spracherkennung musst du das Modell lediglich herunterladen und im Projekt ablegen. Es ist kein Training oder zusätzliche Installation notwendig:

1. Lade das Modell `vosk-model-small-de-0.15` von Vosk Models (https://alphacephei.com/vosk/models) herunter.
2. Entpacke den heruntergeladenen Ordner in dein Projektverzeichnis.
3. Benenne den entpackten Ordner exakt in `model_small` um.

### 4. Ollama einrichten

1. Installiere Ollama für Windows (https://ollama.com/).
2. Öffne dein Terminal und lade das im Code hinterlegte Modell herunter:
```bash
ollama pull gemma4:e2b

```


(Falls du ein anderes Modell wie llama3 nutzen möchtest, passe einfach den Namen im Python-Skript bei OllamaLLM(model="...") an).

---

## Konfiguration

Öffne die Hauptdatei deines Skripts und passe den oberen Konfigurationsblock an deine Umgebung an:

```python
# ==========================================
# KONFIGURATION & GEHEIMNISSE (ZUM ANPASSEN)
# ==========================================
OPENWEATHER_API_KEY = "DEIN_API_KEY_HIER"  # Kostenlos auf openweathermap.org erstellen
LATITUDE = "50.0"                          # Deine Breitengrad-Koordinate
LONGITUDE = "0.0"                         # Deine Längengrad-Koordinate

# Absoluter Pfad zur ollama.exe, damit das Skript Ollama bei Bedarf starten kann
OLLAMA_EXECUTABLE_PATH = r"C:\Pfad\Zu\Deinem\Ollama\ollama.exe"

# Nanoleaf-Name, wie er im Netzwerk erscheint
NANOLEAF_NAME = "Shapes 9121"

# Index des Mikrofon-Eingabegeräts
INPUT_DEVICE_INDEX = 3
# ==========================================

```

### Wie finde ich meinen INPUT_DEVICE_INDEX?

Um herauszufinden, welche Nummer (Index) dein Mikrofon hat, kannst du dieses kurze Hilfsskript in einer separaten Python-Datei ausführen:

```python
import pyaudio

p = pyaudio.PyAudio()
print("Verfügbare Audio-Eingabegeräte:")
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if dev.get('maxInputChannels') > 0:
        print(f"Index {i}: {dev.get('name')}")
p.terminate()

```

Lass dir die Liste im Terminal ausgeben, suche dein gewünschtes Mikrofon und trage die zugehörige Index-Nummer oben bei `INPUT_DEVICE_INDEX` ein.

> Wichtig für Nanoleaf: Beim allerersten Start des Skripts sucht das Programm nach deinem Nanoleaf-Panel. Halte den Power-Button an deinem Nanoleaf-Controller für ca. 5-7 Sekunden gedrückt (bis die LEDs blinken), um den Kopplungsmodus zu aktivieren. Das Skript generiert dann automatisch ein dauerhaftes Authentifizierungs-Token.

---

## Benutzung

Starte das Skript über dein Terminal:

```bash
python main.py

```

Das Skript prüft nun im Hintergrund, ob Ollama läuft (und startet es gegebenenfalls), verbindet sich mit dem Mikrofon über den konfigurierten Index und wartet auf dich.

**Sprachbefehle (Immer mit "Computer" beginnen):**

* "Computer, wie wird das Wetter heute?"
* "Computer, wird es morgen regnen?"
* "Computer, Licht an!" / "Computer, Licht aus!"
* "Computer, warum ist der Himmel blau?" (Leitet die Frage an das lokale KI-Modell weiter)
