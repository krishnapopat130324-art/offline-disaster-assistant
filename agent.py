#!/usr/bin/env python3
"""
🚨 Offline Disaster Assistant - Using sounddevice
"""

import json
import os
import sys
import time
import subprocess
import tempfile
import numpy as np
import sounddevice as sd
import requests

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

print("="*60)
print("🚨 OFFLINE DISASTER ASSISTANT v1.0 (sounddevice)")
print("="*60)
print("Loading components...")

# Check Vosk
VOSK_AVAILABLE = False
try:
    import vosk
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
    print("✅ Vosk (Speech-to-Text) loaded")
except ImportError:
    print("❌ Vosk not installed. Run: pip install vosk")

# Check sounddevice
try:
    print(f"✅ sounddevice loaded (version {sd.__version__})")
    devices = sd.query_devices()
    print(f"   Found {len(devices)} audio devices")
except Exception as e:
    print(f"❌ sounddevice error: {e}")

# Check Ollama
OLLAMA_AVAILABLE = False
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        OLLAMA_AVAILABLE = True
        print("✅ Ollama connected")
    else:
        print("❌ Ollama not responding")
except:
    print("❌ Ollama not running. Start with: ollama serve")

# Check Piper
PIPER_AVAILABLE = False
try:
    piper_path = config.get('piper_model_path', 'models/piper/en_US-amy-low.onnx')
    if os.path.exists(piper_path):
        PIPER_AVAILABLE = True
        print(f"✅ Piper model found")
    else:
        print("❌ Piper model not found")
except:
    print("❌ Piper not available")

print("-"*60)
print(f"STT: {'✅' if VOSK_AVAILABLE else '❌'} Vosk")
print(f"LLM: {'✅' if OLLAMA_AVAILABLE else '❌'} Ollama")
print(f"TTS: {'✅' if PIPER_AVAILABLE else '❌'} Piper")
print("="*60)

def listen_vosk():
    """Listen using Vosk with sounddevice"""
    try:
        model_path = config.get('vosk_model_path', 'models/vosk-model-small-en-us-0.15')
        
        if not os.path.exists(model_path):
            print(f"⚠️ Vosk model not found")
            return input("🎤 Type your question: ")
        
        model = Model(model_path)
        recognizer = KaldiRecognizer(model, 16000)
        
        sample_rate = 16000
        duration = 5  # seconds
        
        print("🎤 Listening... (speak clearly for 5 seconds)")
        
        # Record audio
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='int16'
        )
        sd.wait()
        
        # Process audio
        if recognizer.AcceptWaveform(audio_data.tobytes()):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            if text:
                print(f"📝 You said: {text}")
                return text
        
        result = json.loads(recognizer.FinalResult())
        text = result.get("text", "")
        
        if text:
            print(f"📝 You said: {text}")
            return text
        else:
            print("⚠️ Could not understand audio")
            return input("🎤 Type your question: ")
            
    except Exception as e:
        print(f"⚠️ Voice error: {e}")
        return input("🎤 Type your question: ")

def speak_piper(text):
    """Speak using Piper TTS"""
    try:
        model_path = config.get('piper_model_path', 'models/piper/en_US-amy-low.onnx')
        
        if not os.path.exists(model_path):
            print(f"🤖 {text}")
            return
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            output_file = tmp.name
        
        cmd = ['piper', '--model', model_path, '--output_file', output_file]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        proc.stdin.write(text)
        proc.stdin.close()
        proc.wait(timeout=10)
        
        if proc.returncode == 0 and os.path.exists(output_file):
            os.system(f'start {output_file}')
            time.sleep(2)
            try:
                os.unlink(output_file)
            except:
                pass
        else:
            print(f"🤖 {text}")
            
    except Exception as e:
        print(f"🤖 {text}")

def think_ollama(prompt):
    """Get response from Ollama LLM"""
    if not OLLAMA_AVAILABLE:
        return "⚠️ AI brain not available."
    
    model = config.get('llm_model', 'gemma3:1b')
    url = "http://localhost:11434/api/generate"
    
    system_prompt = """You are a disaster response assistant. Keep responses clear, brief, and actionable. Maximum 3 sentences."""
    full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
    
    try:
        response = requests.post(url, json={
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "temperature": 0.2,
            "max_tokens": 150
        }, timeout=30)
        
        if response.status_code == 200:
            return response.json().get("response", "I couldn't generate a response.").strip()
        else:
            return f"⚠️ API error: {response.status_code}"
    except Exception as e:
        return f"⚠️ Error: {e}"

def main():
    print("\n" + "="*60)
    print("🚨 DISASTER ASSISTANT READY")
    print("="*60)
    print("⚠️  Type 'exit' to quit")
    print("-"*60)
    
    use_voice = VOSK_AVAILABLE
    
    while True:
        print("\n🎤 Waiting for input...")
        
        try:
            if use_voice:
                user_input = listen_vosk()
            else:
                user_input = input("💬 You: ")
            
            if user_input.lower() in ['exit', 'quit', 'goodbye']:
                print("👋 Goodbye! Stay safe.")
                speak_piper("Goodbye! Stay safe.")
                break
            
            if not user_input.strip():
                continue
            
            print("🧠 Processing...")
            response = think_ollama(user_input)
            print(f"🤖 Assistant: {response}")
            speak_piper(response)
            
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            continue

if __name__ == "__main__":
    main()