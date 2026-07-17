from vosk import Model, KaldiRecognizer
import pyaudio
import pyttsx3
import requests
import json
from datetime import date, timedelta
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
import socket
from typing import Dict
from nanoleafapi import Nanoleaf
import socket
from typing import Dict
from zeroconf import Zeroconf, ServiceBrowser, ServiceListener
import time
import subprocess
import time
import os

# ==========================================
# KONFIGURATION & GEHEIMNISSE (ZUM ANPASSEN)
# ==========================================
OPENWEATHER_API_KEY = "DEIN_API_KEY_HIER"
LATITUDE = "50.0"  # Deine Breitengrad-Koordinate
LONGITUDE = "0.0"  # Deine Längengrad-Koordinate

# Absoluter Pfad zur ollama.exe, falls der Standard-Windows-Pfad nicht greift
OLLAMA_EXECUTABLE_PATH = r"C:\Pfad\Zu\Deinem\Ollama\ollama.exe"

#Nanoleaf-Name, wie er im Netzwerk erscheint (z.B. "Shapes 9121")
NANOLEAF_NAME = "Shapes 9121"

# Index des Mikrofon-Eingabegeräts
INPUT_DEVICE_INDEX = 3
# ==========================================

class NanoleafListener(ServiceListener):
    def __init__(self):
        self.found_devices = {}

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        if info:
            dev_name = name.split(".")[0].replace("\\", "")
            
            addresses = info.addresses
            if addresses:
                ip = socket.inet_ntoa(addresses[0])
                self.found_devices[dev_name] = ip

def discover_devices(timeout: int = 5) -> Dict[str, str]:
    zeroconf = Zeroconf()
    listener = NanoleafListener()
    
    browser = ServiceBrowser(zeroconf, "_nanoleafapi._tcp.local.", listener)

    time.sleep(timeout)
    
    zeroconf.close()
    return listener.found_devices

nanoleaf_dict = discover_devices()
nl = Nanoleaf(nanoleaf_dict.get(NANOLEAF_NAME))
nl.check_connection()

if(nl.get_auth_token() == None):
	nl.create_auth_token()

# TTS-Engine einmalig initialisieren
engine = pyttsx3.init()
engine.setProperty('voice', 'de')
engine.setProperty('rate', 225)  # Sprechgeschwindigkeit
engine.setProperty('volume', 1.0)  # Lautstärke (0.0 bis 1.0)

url = f"https://api.openweathermap.org/data/2.5/weather?lat={LATITUDE}&lon={LONGITUDE}&lang=de&units=metric&appid={OPENWEATHER_API_KEY}"
urlForcast = f"https://api.openweathermap.org/data/2.5/forecast?lat={LATITUDE}&lon={LONGITUDE}&lang=de&units=metric&appid={OPENWEATHER_API_KEY}"

# Prompt & LLM
template = """
Du darfst nur Deutsch sprechen, dies erwähnst du auch nicht, da dies bereits der Benutzer weiß. Beantworte die Frage in maximal 2 kurzen Sätzen, ohne den Prompt zu wiederholen. Präzise Antworten!
Frage: "{question}"
Antwort:
"""
ollamaModel = OllamaLLM(model="gemma4:e2b")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | ollamaModel


def kelvin_to_celsius(kelvin: float) -> float:
    return kelvin - 273.15

def handleWeatherHeute(data:json) -> str:
    main_info = data.get('main', {})
    t_min_k = main_info.get('temp_min')
    t_max_k = main_info.get('temp_max')

    if t_min_k is None or t_max_k is None:
        print("Keine temp_min/temp_max Daten in der JSON.")
        return

    # Umrechnung in °C
    t_min_c = kelvin_to_celsius(t_min_k)
    t_max_c = kelvin_to_celsius(t_max_k)

    description = data.get('weather', [{}])[0].get('description', 'keine Angabe')

    return str(f"""Heute wird es {description} und es ergeben sich Temperaturen von einem
     Tiefstwert von {t_min_c:.1f} Grad und einem
     Höchstwert von {t_max_c:.1f} Grad.
    """)

def handleWeatherMorgen(data: json) -> str:
    morgen = date.today() + timedelta(days=1)
    morgen_str = morgen.isoformat()

    temps = []
    descriptions = []
    for entry in data.get('list', []):
        dt_txt = entry.get('dt_txt')
        if dt_txt and dt_txt.startswith(morgen_str):
            temps.append(entry['main']['temp'])
            desc = entry.get('weather', [{}])[0].get('description', 'keine Angabe')
            descriptions.append(desc)

    if not temps:
        return f"Keine Einträge für {morgen_str} gefunden."

    t_min_k = min(temps)
    t_max_k = max(temps)
    t_min_c = kelvin_to_celsius(t_min_k)
    t_max_c = kelvin_to_celsius(t_max_k)

    unique_desc = sorted(set(descriptions))
    desc_text = ', '.join(unique_desc)

    return str(
        f"Morgen wird es {desc_text} und "
        f"es ergeben sich Temperaturen von einem\n"
        f"  Tiefstwert von {t_min_c:.1f} Grad und einem\n"
        f"  Höchstwert von {t_max_c:.1f} Grad."
    )


def average_rainfall_today(current_data: json) -> str:
    rain = current_data.get('rain', {})
    avg_today = float(rain.get('1h', rain.get('3h', 0.0)))
    return f"Durchschnittlicher Niederschlag heute beträgt {avg_today:.2f}  Millimeter"

def average_rainfall_tomorrow(forecast_data: json) -> str:
    morgen = date.today() + timedelta(days=1)
    morgen_str = morgen.isoformat()  # z.B. "2025-07-25"

    rain_values = []
    for entry in forecast_data.get('list', []):
        if entry.get('dt_txt', '').startswith(morgen_str):
            rain_mm = entry.get('rain', {}).get('3h', 0.0)
            rain_values.append(rain_mm)

    if not rain_values:
        return 0.0
    avg_tomorrow = sum(rain_values) / len(rain_values)
    return f"Durchschnittlicher Niederschlag morgen beträgt {avg_tomorrow:.2f}  Millimeter"


def processText(text: str):
    lower = text.lower()
    key = "computer"
    idx = lower.find(key)
    if idx != -1:
        new_text = text[idx + len(key):].lstrip()
        handle_conversation(new_text)

def handle_conversation(text: str):
    if "wetter" in text:
        if "morgen" in text:
            response = requests.get(urlForcast).json()
            print(response)
            engine.say(str(handleWeatherMorgen(response)))
            engine.runAndWait()
            print(response)
            engine.say(str(handleWeatherHeute(response)))
            engine.runAndWait()
    elif "regnen" in text or "regen" in text:
        if "morgen" in text:
            response = requests.get(urlForcast).json()
            print(response)
            engine.say(str(average_rainfall_tomorrow(response)))
            engine.runAndWait()
        else:
            response = requests.get(url).json()
            print(response)
            engine.say(str(average_rainfall_today(response)))
            engine.runAndWait()
    elif "licht" in text or "lichter" in text or "nicht" in text:
        if "an" in text:
            nl.power_on()
            print("AI: An")
        elif "aus" in text:
            nl.power_off()
            print("AI: Aus")
        else:
            engine.say("Ich habe das leider nicht verstanden")
            engine.runAndWait()
    else:
        print("↻Loading")
        result = chain.invoke({"question": text})
        print("AI:", result)
        engine.say(result)
        engine.runAndWait()


# Voice-to-Text mit Vosk
model = Model("model_small")
mic = pyaudio.PyAudio()
recognizer = KaldiRecognizer(model, 48000)

stream = mic.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=48000,
    input=True,
    input_device_index=INPUT_DEVICE_INDEX,
    frames_per_buffer=1024
)
stream.start_stream()

def start_ollama_if_needed():
    print("Prüfe, ob Ollama läuft...")
    try:
        output = subprocess.check_output('tasklist /FI "IMAGENAME eq ollama app.exe"', shell=True, encoding='utf-8', errors='ignore')
        
        if "ollama app.exe" not in output.lower():
            print("Ollama wurde nicht gefunden. Starte Ollama...")
            subprocess.Popen([OLLAMA_EXECUTABLE_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Ollama wird gestartet. Warte 5 Sekunden, bis der Server bereit ist...")
            time.sleep(5)
        else:
            print("Ollama läuft bereits!")
    except Exception as e:
        print(f"Fehler bei der Ollama-Prüfung oder beim Starten: {e}")

start_ollama_if_needed()

while True:
    data = stream.read(1024, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        text = recognizer.Result()[14:-3]
        print("User:", text)
        processText(text)
