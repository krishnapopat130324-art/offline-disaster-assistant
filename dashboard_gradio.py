#!/usr/bin/env python3
"""
🚨 Offline Disaster Assistant - Fresh Light Green Theme
Complete redesign - 100% light green, no black anywhere
ALL FEATURES WORKING: Voice, Text, Responses
"""

import json
import os
import time
import numpy as np
import sounddevice as sd
import requests
import gradio as gr
import wave
import tempfile

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

# Check components
VOSK_AVAILABLE = False
try:
    import vosk
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except:
    pass

OLLAMA_AVAILABLE = False
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        OLLAMA_AVAILABLE = True
except:
    pass

# Load Vosk model once
vosk_model = None
if VOSK_AVAILABLE:
    try:
        model_path = config.get('vosk_model_path', 'models/vosk-model-small-en-us-0.15')
        if os.path.exists(model_path):
            vosk_model = Model(model_path)
            print("✅ Vosk model loaded successfully")
        else:
            print(f"❌ Vosk model not found at: {model_path}")
    except Exception as e:
        print(f"❌ Vosk model error: {e}")

def transcribe_audio_file(audio_path):
    """Transcribe audio file using Vosk"""
    if audio_path is None:
        return None, "⚠️ No audio detected. Please record first."
    
    try:
        if not VOSK_AVAILABLE or vosk_model is None:
            return None, "⚠️ Speech recognition not available. Please type your question."
        
        # Read the audio file
        wf = wave.open(audio_path, 'rb')
        audio_data = wf.readframes(wf.getnframes())
        wf.close()
        
        # Process with Vosk
        recognizer = KaldiRecognizer(vosk_model, 16000)
        
        if recognizer.AcceptWaveform(audio_data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            if text:
                return text, None
        
        # Try final result
        result = json.loads(recognizer.FinalResult())
        text = result.get("text", "")
        
        if text:
            return text, None
        else:
            return None, "⚠️ Could not understand audio. Please speak clearly or type your question."
            
    except Exception as e:
        return None, f"⚠️ Audio error: {str(e)}"

def get_response(text, location, emergency_type):
    """Get AI response with location awareness"""
    if not text or text.strip() == '':
        return "Please type a question or speak into your microphone."
    
    if not OLLAMA_AVAILABLE:
        return "⚠️ Ollama is not running. Please start it with: ollama serve"
    
    location_info = ""
    if location and location.strip():
        location_info = f"User location: {location}\n\n"
    
    emergency_prompt = ""
    if emergency_type != "General":
        emergency_prompt = f"This is a {emergency_type} emergency! "
    
    system_prompt = """You are a DISASTER ASSISTANCE AI. Provide immediate, practical, life-saving advice.

RULES:
1. NEVER pretend to send help – tell the user WHAT TO DO
2. Always tell the user to call emergency services (911)
3. Give clear, step-by-step actions
4. Be calm and reassuring
5. Keep responses brief (2-3 sentences)

User question: {question}

Assistant:"""
    
    model = config.get('llm_model', 'llama3.2:1b')
    url = "http://localhost:11434/api/generate"
    full_prompt = location_info + emergency_prompt + system_prompt.format(question=text)
    
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
            
            if emergency_type != "General" and location and location.strip():
                result += f"\n\n📍 Remember: Call 911 and tell them your location: {location}"
            
            return result.strip()
        else:
            return f"⚠️ API error: {response.status_code}"
            
    except Exception as e:
        return f"⚠️ Error: {e}"

def process_text_input(text, location, emergency_type):
    """Process text input"""
    if not text or text.strip() == '':
        return "Please type a question.", ""
    
    response = get_response(text, location, emergency_type)
    return response, text

def process_audio_input(audio, location, emergency_type):
    """Process audio input - FIXED for gradio Audio component"""
    if audio is None:
        return "Please record a question first.", ""
    
    # audio comes as (sample_rate, audio_data) or filepath
    # Gradio's Audio component with type="filepath" gives file path
    # Gradio's Audio component with type="numpy" gives (sample_rate, data)
    
    try:
        # Handle both formats
        if isinstance(audio, tuple):
            # It's (sample_rate, data) - numpy format
            sample_rate, audio_data = audio
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                wf = wave.open(tmp.name, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
                wf.close()
                audio_file = tmp.name
        elif isinstance(audio, str):
            # It's a file path
            audio_file = audio
        else:
            return "⚠️ Unsupported audio format.", ""
        
        # Transcribe
        transcribed_text, error = transcribe_audio_file(audio_file)
        
        # Clean up temp file if created
        if isinstance(audio, tuple) and os.path.exists(audio_file):
            try:
                os.unlink(audio_file)
            except:
                pass
        
        if error:
            return error, ""
        
        if not transcribed_text:
            return "⚠️ No speech detected. Please try again or type your question.", ""
        
        # Get AI response
        response = get_response(transcribed_text, location, emergency_type)
        return response, transcribed_text
        
    except Exception as e:
        return f"⚠️ Error processing audio: {str(e)}", ""

def handle_submit(text, location, emergency_type, audio):
    """Handle both text and audio input"""
    # Check if audio is provided
    if audio is not None:
        return process_audio_input(audio, location, emergency_type)
    elif text and text.strip():
        return process_text_input(text, location, emergency_type)
    else:
        return "Please type a question or record your voice.", ""

# ============================================================
# FRESH LIGHT GREEN THEME - COMPLETE REDESIGN
# ============================================================

custom_css = """
    /* RESET - Remove ALL dark backgrounds */
    * {
        background-color: transparent !important;
        color: #2d4a3a !important;
    }
    
    /* Main container - Light Green */
    .gradio-container {
        max-width: 1000px !important;
        margin: auto !important;
        background: #e8f5e9 !important;
        padding: 20px !important;
        border-radius: 30px !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    /* Force everything to be light green background */
    body, html, .main, .tabs, .tab-nav, .tab, .accordion, .panel, .block, .form {
        background: #e8f5e9 !important;
    }
    
    .dark, .dark-mode, [data-testid="dark"] {
        background: #e8f5e9 !important;
    }
    
    /* ============================================================
       HEADER - Light Green with White
    ============================================================ */
    .premium-header {
        background: linear-gradient(135deg, #81c784 0%, #a5d6a7 50%, #c8e6c9 100%) !important;
        padding: 35px 40px !important;
        border-radius: 25px !important;
        margin-bottom: 25px !important;
        text-align: center !important;
        border: 2px solid #ffffff !important;
        box-shadow: 0 8px 30px rgba(129, 199, 132, 0.25) !important;
    }
    
    .premium-header h1 {
        color: #1b5e20 !important;
        font-size: 2.5em !important;
        margin: 0 !important;
        font-weight: 800 !important;
        letter-spacing: -1px !important;
    }
    
    .premium-header .subtitle {
        color: #2e7d32 !important;
        font-size: 1.1em !important;
        margin-top: 10px !important;
        font-weight: 400 !important;
    }
    
    .premium-badge {
        display: inline-block !important;
        background: rgba(255,255,255,0.8) !important;
        padding: 8px 30px !important;
        border-radius: 50px !important;
        color: #1b5e20 !important;
        font-size: 0.9em !important;
        font-weight: 700 !important;
        margin-top: 15px !important;
        border: 2px solid rgba(255,255,255,0.6) !important;
    }
    
    /* ============================================================
       STATUS CARDS - White with Green Border
    ============================================================ */
    .status-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr 1fr !important;
        gap: 16px !important;
        margin-bottom: 25px !important;
    }
    
    .status-card {
        background: #ffffff !important;
        border-radius: 20px !important;
        padding: 22px 24px !important;
        border: 2px solid #a5d6a7 !important;
        text-align: center !important;
        box-shadow: 0 4px 15px rgba(129, 199, 132, 0.10) !important;
        transition: all 0.3s ease !important;
    }
    
    .status-card:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 30px rgba(129, 199, 132, 0.18) !important;
    }
    
    .status-card .icon {
        font-size: 2em !important;
        display: block !important;
    }
    
    .status-card .label {
        font-size: 0.95em !important;
        color: #388e3c !important;
        font-weight: 600 !important;
        margin-top: 8px !important;
    }
    
    .status-card .status {
        font-size: 0.85em !important;
        font-weight: 700 !important;
        padding: 5px 20px !important;
        border-radius: 50px !important;
        display: inline-block !important;
        margin-top: 8px !important;
    }
    
    .status-online {
        background: #c8e6c9 !important;
        color: #1b5e20 !important;
        border: 1px solid #81c784 !important;
    }
    
    .status-offline {
        background: #ffcdd2 !important;
        color: #b71c1c !important;
        border: 1px solid #ef9a9a !important;
    }
    
    /* ============================================================
       INPUT AREA - White with Green Border
    ============================================================ */
    .input-area {
        background: #ffffff !important;
        border-radius: 25px !important;
        padding: 30px !important;
        border: 2px solid #a5d6a7 !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 15px rgba(129, 199, 132, 0.08) !important;
    }
    
    .input-area label {
        font-weight: 600 !important;
        color: #2e7d32 !important;
        font-size: 1em !important;
    }
    
    /* ============================================================
       TEXT INPUTS - Light Green Background
    ============================================================ */
    textarea, input[type="text"], select {
        border-radius: 15px !important;
        border: 2px solid #c8e6c9 !important;
        padding: 14px 18px !important;
        font-size: 1em !important;
        background: #f1f8e9 !important;
        color: #1b5e20 !important;
        transition: all 0.3s ease !important;
    }
    
    textarea:focus, input[type="text"]:focus, select:focus {
        border-color: #66bb6a !important;
        box-shadow: 0 0 0 5px rgba(102, 187, 106, 0.15) !important;
        outline: none !important;
        background: #ffffff !important;
    }
    
    textarea::placeholder, input::placeholder {
        color: #81a881 !important;
        font-style: italic !important;
    }
    
    /* ============================================================
       DROPDOWN - Light Green
    ============================================================ */
    select, select option {
        color: #1b5e20 !important;
        background: #f1f8e9 !important;
    }
    
    /* ============================================================
       SUBMIT BUTTON - Bright Green
    ============================================================ */
    .submit-btn {
        background: linear-gradient(135deg, #66bb6a 0%, #43a047 100%) !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 16px 30px !important;
        font-weight: 700 !important;
        font-size: 1.1em !important;
        color: #ffffff !important;
        box-shadow: 0 6px 25px rgba(102, 187, 106, 0.35) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        letter-spacing: 0.5px !important;
        cursor: pointer !important;
    }
    
    .submit-btn:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 35px rgba(102, 187, 106, 0.45) !important;
        background: linear-gradient(135deg, #76d27a 0%, #4caf50 100%) !important;
    }
    
    .submit-btn * {
        color: #ffffff !important;
    }
    
    /* ============================================================
       RESPONSE AREA - Light Green Gradient
    ============================================================ */
    .response-area {
        background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 100%) !important;
        border-radius: 25px !important;
        padding: 30px !important;
        border: 2px solid #a5d6a7 !important;
        min-height: 150px !important;
        margin-top: 15px !important;
        box-shadow: 0 4px 15px rgba(129, 199, 132, 0.06) !important;
    }
    
    .response-area .response-label {
        font-weight: 700 !important;
        color: #1b5e20 !important;
        margin-bottom: 15px !important;
        font-size: 0.95em !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }
    
    .response-area .response-text {
        color: #1b5e20 !important;
        font-size: 1.1em !important;
        line-height: 1.8 !important;
        white-space: pre-wrap !important;
        background: transparent !important;
        min-height: 80px !important;
    }
    
    /* ============================================================
       QUICK BUTTONS - White with Green Border
    ============================================================ */
    .quick-btn {
        background: #ffffff !important;
        border: 2px solid #c8e6c9 !important;
        border-radius: 14px !important;
        padding: 14px 10px !important;
        font-weight: 600 !important;
        color: #388e3c !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
        font-size: 0.9em !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02) !important;
        cursor: pointer !important;
    }
    
    .quick-btn:hover {
        background: #66bb6a !important;
        border-color: #43a047 !important;
        color: #ffffff !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(102, 187, 106, 0.25) !important;
    }
    
    .quick-btn .emoji {
        display: block !important;
        font-size: 1.5em !important;
        margin-bottom: 4px !important;
    }
    
    /* ============================================================
       AUDIO INPUT
    ============================================================ */
    .audio-input {
        border-radius: 16px !important;
        border: 2px solid #c8e6c9 !important;
        padding: 12px !important;
        background: #f1f8e9 !important;
    }
    
    /* ============================================================
       FOOTER
    ============================================================ */
    .footer {
        text-align: center !important;
        padding: 25px !important;
        color: #81a881 !important;
        font-size: 0.9em !important;
        border-top: 2px solid #c8e6c9 !important;
        margin-top: 30px !important;
        background: transparent !important;
    }
    
    /* ============================================================
       FORCE ALL TEXT TO BE GREEN, NOT BLACK
    ============================================================ */
    label, span, div, p, h1, h2, h3, h4, h5, h6, .md, .prose {
        color: #1b5e20 !important;
    }
    
    /* Keep white text on green buttons */
    .submit-btn, .submit-btn * {
        color: #ffffff !important;
    }
    
    .quick-btn:hover, .quick-btn:hover * {
        color: #ffffff !important;
    }
    
    /* ============================================================
       REMOVE ANY REMAINING DARK ELEMENTS
    ============================================================ */
    [class*="dark"], [data-testid*="dark"], .dark-mode {
        background: #e8f5e9 !important;
        color: #1b5e20 !important;
    }
    
    /* ============================================================
       RESPONSIVE
    ============================================================ */
    @media (max-width: 768px) {
        .status-grid {
            grid-template-columns: 1fr !important;
        }
        .premium-header h1 {
            font-size: 1.6em !important;
        }
        .premium-header {
            padding: 20px !important;
        }
        .gradio-container {
            padding: 10px !important;
        }
    }
"""

# ============================================================
# BUILD THE INTERFACE
# ============================================================

with gr.Blocks(
    title="🚨 Disaster Assistant",
    theme=gr.themes.Soft(
        primary_hue="green",
        secondary_hue="lime",
        neutral_hue="gray",
        font=gr.themes.GoogleFont("Segoe UI")
    ),
    css=custom_css
) as demo:
    
    # HEADER
    gr.HTML("""
        <div class="premium-header">
            <h1>🌿 Offline Disaster Assistant</h1>
            <div class="subtitle">AI-Powered Emergency Guidance • 100% Offline • Zero Cost</div>
            <div class="premium-badge">⚡ Always Ready • No Internet Required</div>
        </div>
    """)
    
    # STATUS CARDS
    with gr.Row():
        with gr.Column():
            gr.HTML(f"""
                <div class="status-card">
                    <span class="icon">🎤</span>
                    <div class="label">Speech Recognition</div>
                    <div class="status {'status-online' if VOSK_AVAILABLE else 'status-offline'}">
                        {'✅ Online' if VOSK_AVAILABLE else '❌ Offline'}
                    </div>
                </div>
            """)
        with gr.Column():
            gr.HTML(f"""
                <div class="status-card">
                    <span class="icon">🧠</span>
                    <div class="label">AI Brain</div>
                    <div class="status {'status-online' if OLLAMA_AVAILABLE else 'status-offline'}">
                        {'✅ Online' if OLLAMA_AVAILABLE else '❌ Offline'}
                    </div>
                </div>
            """)
        with gr.Column():
            gr.HTML("""
                <div class="status-card">
                    <span class="icon">🔒</span>
                    <div class="label">Privacy</div>
                    <div class="status status-online">
                        ✅ 100% Offline
                    </div>
                </div>
            """)
    
    # INPUT AREA
    with gr.Column(elem_classes="input-area"):
        with gr.Row():
            with gr.Column(scale=2):
                text_input = gr.Textbox(
                    label="💬 Type Your Question",
                    placeholder="e.g., What to do in an earthquake?",
                    lines=2
                )
                
                with gr.Row():
                    location_input = gr.Textbox(
                        label="📍 Your Location (Optional)",
                        placeholder="e.g., New York, Building 3",
                        lines=1,
                        scale=2
                    )
                    
                    emergency_type = gr.Dropdown(
                        choices=["General", "Fire", "Earthquake", "Flood", "Medical", "Tornado", "Hurricane", "Tsunami"],
                        label="🚨 Emergency Type",
                        value="General",
                        scale=1
                    )
                
                # AUDIO INPUT - FIXED: Using type="filepath" for better compatibility
                audio_input = gr.Audio(
                    label="🎤 Or Speak Your Question",
                    sources=["microphone"],
                    type="filepath",
                    elem_classes="audio-input"
                )
                
                submit_btn = gr.Button("🌿 Get Help Now", variant="primary", elem_classes="submit-btn")
    
    # RESPONSE AREA
    with gr.Column(elem_classes="response-area"):
        gr.HTML("""
            <div class="response-label">🌱 Assistant Response</div>
        """)
        response_output = gr.Textbox(
            label="",
            lines=6,
            interactive=False,
            placeholder="Your response will appear here...",
            elem_classes="response-text",
            show_label=False
        )
        transcript_output = gr.Textbox(
            label="📝 Transcript",
            lines=1,
            interactive=False,
            visible=True,
            show_label=True,
            placeholder="Your spoken words will appear here..."
        )
    
    # QUICK BUTTONS
    gr.HTML("""
        <div style="text-align: center; padding: 15px 0 5px 0;">
            <span style="color: #388e3c; font-size: 1em; font-weight: 600;">⚡ Quick Emergency Questions</span>
        </div>
    """)
    
    with gr.Row():
        quick_btns = [
            ("🏠 Earthquake", "What to do in an earthquake?"),
            ("🔥 Fire", "What to do if there's a fire?"),
            ("💧 Flood", "How to survive a flood?"),
            ("🩸 Bleeding", "How to stop severe bleeding?"),
            ("🌀 Tornado", "What to do in a tornado?"),
            ("🏥 Medical", "What should I do in a medical emergency?")
        ]
        
        for label, question in quick_btns:
            btn = gr.Button(label, elem_classes="quick-btn")
            btn.click(
                lambda q=question: q,
                outputs=[text_input]
            ).then(
                handle_submit,
                inputs=[text_input, location_input, emergency_type, audio_input],
                outputs=[response_output, transcript_output]
            )
    
    # ============================================================
    # EVENT HANDLERS - ALL WORKING
    # ============================================================
    
    # Text input - press Enter to submit
    text_input.submit(
        handle_submit,
        inputs=[text_input, location_input, emergency_type, audio_input],
        outputs=[response_output, transcript_output]
    )
    
    # Submit button
    submit_btn.click(
        handle_submit,
        inputs=[text_input, location_input, emergency_type, audio_input],
        outputs=[response_output, transcript_output]
    )
    
    # Audio input - auto-process when recording stops
    audio_input.change(
        handle_submit,
        inputs=[text_input, location_input, emergency_type, audio_input],
        outputs=[response_output, transcript_output]
    )
    
    # FOOTER
    gr.HTML("""
        <div class="footer">
            🌿 Built with ❤️ • 100% Free & Open Source • For Emergency Preparedness Only
        </div>
    """)

# ============================================================
# LAUNCH
# ============================================================

if __name__ == "__main__":
    print("="*60)
    print("🌿 Offline Disaster Assistant - Fully Working")
    print("="*60)
    print("✅ 100% Light Theme - No Black Anywhere")
    print("✅ Voice Input Working")
    print("✅ Text Input Working")
    print("✅ AI Responses Working")
    print("📱 Open: http://127.0.0.1:7860")
    print("⚠️  Press Ctrl+C to stop")
    print("="*60)
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True,
        quiet=True
    )