# AI-Computer (Local Offline Voice Assistant)

This project implements a privacy-focused, local voice assistant for Windows. It listens for the wake-word "Computer", responds using a synthetic Text-to-Speech (TTS) voice, fetches weather data via an API, and controls Nanoleaf lights within your local network. Complex open-ended questions are processed entirely locally using Ollama.
It's main use is in German, but you can change it to your language in the code.

## Features
- 100% Local Speech-to-Text (STT): Powered by Vosk for offline speech recognition.
- Local AI Model: Handles general knowledge questions locally via Ollama (gemma4:e2b).
- Weather Integration: Accurate current forecasts and rain reports via OpenWeatherMap.
- Smart Home Control: Automatic discovery and toggling of Nanoleaf devices (e.g., Shapes).
- Text-to-Speech (TTS): Responds directly in German using the system's native voice.

---

## Prerequisites & Installation

### 1. Windows Dependencies (PyAudio)
Since installing PyAudio directly on Windows can sometimes fail, it is highly recommended to install it using pipwin:
```bash
pip install pipwin
pipwin install pyaudio

```

### 2. Install Python Libraries

Install all other required packages with the following command:

```bash
pip install vosk pyttsx3 requests langchain-core langchain-ollama nanoleafapi zeroconf

```

### 3. Download the Vosk Speech Model

For speech recognition to function, you simply need to download the model and place it into your project. No training or extra installation is required:

1. Download the `vosk-model-small-de-0.15` model from Vosk Models (https://alphacephei.com/vosk/models).
2. Extract the downloaded folder into your main project directory.
3. Rename the extracted folder exactly to `model_small`.

### 4. Set Up Ollama

1. Install Ollama for Windows (https://ollama.com/).
2. Open your terminal and download the model specified in the code:
```bash
ollama pull gemma4:e2b

```


(If you prefer to use a different model like llama3, simply change the model name inside the Python script where `OllamaLLM(model="...")` is defined).

---

## Configuration

Open the main file of your script and adjust the configuration block at the top to match your environment:

```python
# ==========================================
# CONFIGURATION & SECRETS (CUSTOMIZE HERE)
# ==========================================
OPENWEATHER_API_KEY = "YOUR_API_KEY_HERE"  # Create for free on openweathermap.org
LATITUDE = "50.0"                          # Your latitude coordinate
LONGITUDE = "0.0"                          # Your longitude coordinate

# Absolute path to ollama.exe so the script can launch Ollama if it isn't running
OLLAMA_EXECUTABLE_PATH = r"C:\Path\To\Your\Ollama\ollama.exe"

# Nanoleaf name as it appears in your network
NANOLEAF_NAME = "Shapes 9121"

# Index of your microphone input device
INPUT_DEVICE_INDEX = 3
# ==========================================

```

### How to find your INPUT_DEVICE_INDEX

To find out which ID (index) belongs to your microphone, you can run this short helper script in a separate Python file:

```python
import pyaudio

p = pyaudio.PyAudio()
print("Available audio input devices:")
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if dev.get('maxInputChannels') > 0:
        print(f"Index {i}: {dev.get('name')}")
p.terminate()

```

Run the script, check the terminal output for your desired microphone, and enter its corresponding index number into the `INPUT_DEVICE_INDEX` variable above.

> Important for Nanoleaf: During the very first launch, the program will look for your Nanoleaf panel. Press and hold the power button on your Nanoleaf controller for about 5-7 seconds (until the LEDs start flashing) to enable pairing mode. The script will then automatically generate a permanent authentication token.

---

## Usage

Start the script via your terminal:

```bash
python main.py

```

The script will check in the background if Ollama is running (and launch it if necessary), connect to your microphone using the configured index, and start listening for your commands.

**Voice Commands (Always start with "Computer"):**

* "Computer, wie wird das Wetter heute?" (Computer, how is the weather today?)
* "Computer, wird es morgen regnen?" (Computer, will it rain tomorrow?)
* "Computer, Licht an!" / "Computer, Licht aus!" (Computer, turn the light on! / turn the light off!)
* "Computer, warum ist der Himmel blau?" (Computer, why is the sky blue? -> forwards the question to your local AI model)

