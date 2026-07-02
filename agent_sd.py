#!/usr/bin/env python3
"""
🚨 Offline Disaster Assistant - With Smart Location Detection
Asks for location only when needed for emergency response
"""

import json
import os
import sys
import time
import numpy as np
import sounddevice as sd
import requests

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

print("="*60)
print("🚨 OFFLINE DISASTER ASSISTANT v1.0 (Smart Location)")
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
except Exception as e:
    print(f"❌ Vosk error: {e}")

# Check sounddevice
try:
    print(f"✅ sounddevice loaded (version {sd.__version__})")
    devices = sd.query_devices()
    print(f"   Found {len(devices)} audio devices")
    default_device = sd.query_devices(kind='input')
    print(f"   Default microphone: {default_device['name']}")
except Exception as e:
    print(f"❌ sounddevice error: {e}")

# Check pyttsx3
TTS_AVAILABLE = False
try:
    import pyttsx3
    TTS_AVAILABLE = True
    print("✅ pyttsx3 loaded (Windows TTS)")
except ImportError:
    print("❌ pyttsx3 not installed. Run: pip install pyttsx3")

# Check Ollama
OLLAMA_AVAILABLE = False
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        OLLAMA_AVAILABLE = True
        print("✅ Ollama connected")
        models = response.json().get('models', [])
        if models:
            print(f"   Available models: {[m['name'] for m in models]}")
    else:
        print("❌ Ollama not responding")
except:
    print("❌ Ollama not running. Start with: ollama serve")

print("-"*60)
print(f"STT: {'✅' if VOSK_AVAILABLE else '❌'} Vosk")
print(f"LLM: {'✅' if OLLAMA_AVAILABLE else '❌'} Ollama")
print(f"TTS: {'✅' if TTS_AVAILABLE else '❌'} pyttsx3")
print("="*60)

def listen_vosk():
    """Listen using Vosk with sounddevice"""
    try:
        model_path = config.get('vosk_model_path', 'models/vosk-model-small-en-us-0.15')
        
        if not os.path.exists(model_path):
            print(f"⚠️ Vosk model not found at {model_path}")
            print("   Download from: https://alphacephei.com/vosk/models")
            print("   Extract to: models/vosk-model-small-en-us-0.15/")
            return input("🎤 Type your question: ")
        
        model = Model(model_path)
        recognizer = KaldiRecognizer(model, 16000)
        
        sample_rate = 16000
        duration = 5
        
        print("🎤 Listening... (speak clearly for 5 seconds)")
        print("   Press Ctrl+C to stop early and type instead")
        
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
            
    except KeyboardInterrupt:
        print("\n⚠️ Recording interrupted")
        return input("🎤 Type your question: ")
    except Exception as e:
        print(f"⚠️ Voice error: {e}")
        return input("🎤 Type your question: ")

def speak_text(text):
    """Speak using pyttsx3 (Windows TTS)"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"🤖 {text}")

def think_ollama(prompt, location=None):
    """Get response from Ollama LLM with location awareness"""
    if not OLLAMA_AVAILABLE:
        return "⚠️ AI brain not available. Please start Ollama."
    
    model = config.get('llm_model', 'llama3.2:1b')
    url = "http://localhost:11434/api/generate"
    
    # Build location-aware prompt
    location_info = ""
    if location:
        location_info = f"User location: {location}\n\n"
    
    system_prompt = """You are a DISASTER ASSISTANCE AI. You provide immediate, practical, life-saving advice.

IMPORTANT RULES:
1. If the user provided a location, USE IT to give specific advice
2. NEVER pretend to send help – instead, tell the user WHAT TO DO
3. Always tell the user to call emergency services (911) for real help
4. Give clear, step-by-step actions
5. Be calm and reassuring
6. Keep responses brief and actionable (2-3 sentences maximum)

EXAMPLES:
- "Apply firm pressure to the wound with a clean cloth. Elevate the wound above heart level. Call 911 immediately."
- "Drop to the ground, take cover under a sturdy table, and hold on. Stay away from windows."
- "Move to higher ground immediately. Turn off electricity. DO NOT walk through flood water."
- "Evacuate the building immediately. Close doors behind you. Call 911 from a safe distance."

User question: {question}

Assistant:"""
    
    full_prompt = location_info + system_prompt.format(question=prompt)
    
    try:
        response = requests.post(
            url,
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "temperature": 0.3,
                "max_tokens": 200
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("response", "I couldn't generate a response.")
            return result.strip()
        else:
            return f"⚠️ API error: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "⚠️ Response timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "⚠️ Cannot connect to Ollama. Make sure it's running."
    except Exception as e:
        return f"⚠️ Error: {e}"

def is_emergency(text):
    """Check if the user input is an emergency requiring location"""
    emergency_keywords = [
        'help', 'emergency', 'trapped', 'bleeding', 'fire', 'flood',
        'earthquake', 'hurt', 'injured', 'danger', 'rescue', 'save',
        'evacuate', 'collapse', 'falling', 'broken', 'bleed',
        'attack', 'accident', 'burn', 'smoke', 'explosion'
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in emergency_keywords)

def is_location_command(text):
    """Check if user is providing location"""
    location_phrases = [
        'my location is', 'i am at', 'i\'m at', 'located at',
        'i am in', 'i\'m in', 'at address', 'at location'
    ]
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in location_phrases)

def extract_location(text):
    """Extract location from user input"""
    text_lower = text.lower()
    for phrase in ['my location is', 'i am at', 'i\'m at', 'located at', 'i am in', 'i\'m in']:
        if phrase in text_lower:
            # Extract everything after the phrase
            parts = text_lower.split(phrase, 1)
            if len(parts) > 1:
                location = parts[1].strip()
                # Clean up
                location = location.rstrip('?.!,').strip()
                return location
    return None

def main():
    """Main application loop with smart location detection"""
    print("\n" + "="*60)
    print("🚨 DISASTER ASSISTANT READY")
    print("="*60)
    print("⚠️  Type 'exit' to quit")
    print("💡  I'll ask for your location ONLY during emergencies")
    print("📍  You can also tell me: 'My location is [your address]'")
    print("")
    print("   Example emergencies:")
    print("   - 'What to do in an earthquake?'")
    print("   - 'How to stop bleeding?'")
    print("   - 'Fire in my house!'")
    print("   - 'I'm trapped!'")
    print("-"*60)
    
    location = None  # No location initially
    use_voice = VOSK_AVAILABLE
    
    while True:
        print("\n" + "-"*60)
        print("🎤 Waiting for input...")
        
        try:
            # Get input
            if use_voice:
                user_input = listen_vosk()
            else:
                user_input = input("💬 You: ")
            
            # Check for exit
            if user_input.lower() in ['exit', 'quit', 'goodbye', 'bye']:
                print("👋 Goodbye! Stay safe out there.")
                speak_text("Goodbye! Stay safe out there.")
                break
            
            if not user_input or user_input.strip() == '':
                print("⚠️ No input detected. Try again.")
                continue
            
            # ============================================
            # SMART LOCATION DETECTION
            # ============================================
            
            # Check if user is providing location
            if is_location_command(user_input):
                new_location = extract_location(user_input)
                if new_location:
                    location = new_location
                    response = f"✅ Location saved: {location}. I'll use this for any emergency advice."
                    print(f"📌 Location set to: {location}")
                else:
                    response = "📍 Please tell me your location. For example: 'My location is 123 Main Street'"
                print(f"🤖 Assistant: {response}")
                speak_text(response)
                continue
            
            # Check if this is an emergency that needs location
            if is_emergency(user_input):
                if not location:
                    print("\n" + "="*60)
                    print("🚨 EMERGENCY DETECTED! I NEED YOUR LOCATION")
                    print("="*60)
                    speak_text("Emergency detected. Please tell me your location.")
                    
                    # Ask for location
                    if use_voice:
                        print("🎤 Please say your location (or type it):")
                        location_input = listen_vosk()
                    else:
                        location_input = input("📍 Please enter your location: ")
                    
                    if location_input and location_input.strip():
                        location = location_input.strip()
                        print(f"📌 Location saved: {location}")
                        speak_text(f"Location saved. I'll use this for your emergency.")
                    else:
                        print("⚠️ No location provided. Continuing without location.")
            
            # ============================================
            # GENERATE RESPONSE
            # ============================================
            
            print("🧠 Processing...")
            response = think_ollama(user_input, location)
            
            # Add location reminder if emergency and location exists
            if is_emergency(user_input) and location:
                reminder = " Remember: Call 911 and tell them your location: " + location
                response = response + reminder
            
            print(f"🤖 Assistant: {response}")
            speak_text(response)
            
            # Show current location status
            if location:
                print(f"📍 Location: {location}")
            else:
                print(f"📍 Location: Not set (tell me: 'My location is...')")
            
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            break
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            continue
    
    print("\n" + "="*60)
    print("✅ Assistant shutdown complete")
    print("="*60)

if __name__ == "__main__":
    main()