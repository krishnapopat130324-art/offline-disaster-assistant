# 🌿 Offline Disaster Assistant

<div align="center">

### AI-Powered Emergency Guidance That Works Without the Internet

**100% Local • 100% Private • 100% Free**

An intelligent offline emergency assistant designed to provide disaster guidance through voice and text interactions, even in areas without internet connectivity. Powered entirely by local AI models for maximum privacy and reliability during critical situations.

</div>

---

## ✨ Features

| Feature                          | Description                                                       |
| -------------------------------- | ----------------------------------------------------------------- |
| 🎤 **Offline Voice Recognition** | Speech-to-text using Vosk with no internet dependency             |
| 🧠 **Local AI Engine**           | Powered by Ollama and Llama 3.2 for completely private processing |
| 🔊 **Text-to-Speech Responses**  | Reads emergency instructions aloud using pyttsx3                  |
| 📍 **Location Awareness**        | Generates context-aware responses based on user location          |
| 🌐 **Fully Offline Operation**   | Works without cloud services or internet access                   |
| 🔒 **Privacy First**             | No data collection, analytics, or external APIs                   |
| ⚡ **Quick Emergency Actions**    | One-click emergency guidance for common situations                |
| 📝 **Conversation Transcript**   | Displays recognized speech and responses in real time             |
| 💚 **Accessible Interface**      | Clean, lightweight, and easy-to-use design                        |

---

## 🚀 Quick Start

### Prerequisites

* Python 3.8 or higher
* Ollama installed locally
* Minimum 2GB RAM (4GB recommended)

### Installation

#### Clone the Repository

```bash
git clone https://github.com/krishnapopat130324-art/offline-disaster-assistant.git
cd offline-disaster-assistant
```

#### Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Download the Local AI Model

```bash
ollama pull llama3.2:1b
```

#### Run the Application

```bash
python dashboard_gradio.py
```

---

## 📖 Usage

### Text Input

Ask emergency questions directly through the text interface.

Example:

```text
What should I do during an earthquake?
```

### Voice Input

* Click the microphone button.
* Speak clearly for a few seconds.
* The assistant automatically converts speech to text and generates a response.

### Quick Emergency Actions

Available emergency categories include:

* 🏠 Earthquake
* 🔥 Fire
* 💧 Flood
* 🩸 Bleeding
* 🌀 Tornado
* 🏥 Medical Emergency

### Location Context

Users can optionally provide their location for more relevant emergency recommendations.

Example:

```text
Apartment Building, New York
```

---

## 🛠️ Tech Stack

| Component            | Technology  |
| -------------------- | ----------- |
| Programming Language | Python 3.8+ |
| User Interface       | Gradio      |
| Speech Recognition   | Vosk        |
| AI Runtime           | Ollama      |
| Language Model       | Llama 3.2   |
| Text-to-Speech       | pyttsx3     |
| Audio Processing     | sounddevice |

---

## 🏗️ System Architecture

```text
User Input
    │
    ├── Text Input
    └── Voice Input
            │
            ▼
    Vosk Speech Recognition
            │
            ▼
      Ollama + Llama 3.2
            │
            ▼
     Emergency Response
            │
            ▼
    pyttsx3 Text-to-Speech
```

---

## 📁 Project Structure

```text
offline-disaster-assistant/
│
├── dashboard_gradio.py
├── config.json
├── requirements.txt
├── README.md
├── setup.bat
├── run.bat
│
└── models/
    └── vosk-model-small-en-us-0.15/
```

---

## ⚙️ Configuration

Example configuration:

```json
{
  "llm_model": "llama3.2:1b",
  "llm_url": "http://localhost:11434",
  "vosk_model_path": "models/vosk-model-small-en-us-0.15",
  "language": "en-US",
  "sample_rate": 16000,
  "max_listen_seconds": 5
}
```

---

## 🎯 Example Responses

| Emergency Situation | Example Guidance                                                          |
| ------------------- | ------------------------------------------------------------------------- |
| Earthquake          | Drop, Cover, and Hold On. Stay away from windows and heavy objects.       |
| Severe Bleeding     | Apply firm pressure and seek immediate medical assistance.                |
| House Fire          | Evacuate immediately and contact emergency services from a safe location. |
| Building Collapse   | Stay calm, conserve energy, and signal for help if possible.              |

---

## 📊 Performance

| Metric                | Value       |
| --------------------- | ----------- |
| Average Response Time | 2–5 seconds |
| RAM Usage             | ~1.5 GB     |
| Storage Requirement   | ~2 GB       |
| Processing Mode       | Fully Local |

---

## 🌍 Real-World Use Cases

* 🏔️ Mountain rescue operations
* 🌊 Flood response support
* 🏕️ Disaster relief camps
* 🚑 Emergency medical triage
* 📡 Areas with poor connectivity
* 🏫 Disaster preparedness training

---

## 🔒 Privacy & Security

✅ No internet required
✅ No cloud services
✅ No tracking or analytics
✅ No API keys
✅ Complete local processing
✅ Open-source and transparent

---

<div align="center">

### 🌿 Built for Reliability When Connectivity Cannot Be Trusted

**Offline AI for emergency preparedness and disaster response.**

Made with ❤️ by Krishna Popat

</div>
