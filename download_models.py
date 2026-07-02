#!/usr/bin/env python3
"""
Helper script to download required models
"""

import os
import zipfile
import requests
import shutil
from pathlib import Path

def download_file(url, filename):
    """Download a file with progress bar"""
    print(f"📥 Downloading {filename}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"✅ Downloaded {filename}")
    return filename

def extract_zip(zip_path, extract_to):
    """Extract a zip file"""
    print(f"📦 Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"✅ Extracted to {extract_to}")

def main():
    print("="*60)
    print("📥 MODEL DOWNLOAD HELPER")
    print("="*60)
    
    # Create directories
    os.makedirs('models', exist_ok=True)
    
    # Vosk model
    print("\n[1/2] Downloading Vosk model...")
    vosk_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    vosk_zip = "models/vosk-model-small-en-us-0.15.zip"
    
    if not os.path.exists('models/vosk-model-small-en-us-0.15'):
        download_file(vosk_url, vosk_zip)
        extract_zip(vosk_zip, 'models/')
        os.remove(vosk_zip)
    else:
        print("✅ Vosk model already exists")
    
    # Piper model
    print("\n[2/2] Downloading Piper model...")
    os.makedirs('models/piper', exist_ok=True)
    
    piper_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx"
    piper_path = "models/piper/en_US-amy-low.onnx"
    
    if not os.path.exists(piper_path):
        download_file(piper_url, piper_path)
    else:
        print("✅ Piper model already exists")
    
    print("\n" + "="*60)
    print("✅ ALL MODELS DOWNLOADED!")
    print("="*60)
    print("\nRun the assistant:")
    print("  python agent.py")

if __name__ == "__main__":
    main()