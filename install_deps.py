import subprocess
import sys
import platform

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install packages
packages = [
    "vosk",
    "pyaudio",
    "requests",
    "pygame"
]

print("📦 Installing dependencies...")
for pkg in packages:
    print(f"Installing {pkg}...")
    try:
        install_package(pkg)
        print(f"✅ {pkg} installed")
    except:
        print(f"❌ Failed to install {pkg}")

print("\n✅ Installation complete!")
print("Run: python agent.py")