#!/usr/bin/env python3
"""
Ollama installation script for cross-platform support.
"""
import os
import sys
import platform
import subprocess
import urllib.request
import zipfile
import tarfile
from pathlib import Path

def get_system_info():
    """Get system information for platform-specific installation."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if machine in ['x86_64', 'amd64']:
        arch = 'amd64'
    elif machine in ['arm64', 'aarch64']:
        arch = 'arm64'
    else:
        arch = machine
    
    return system, arch

def install_ollama_macos():
    """Install Ollama on macOS."""
    print("🍎 Installing Ollama for macOS...")
    
    # Check if Homebrew is available
    try:
        subprocess.run(['brew', '--version'], check=True, capture_output=True)
        print("📦 Installing via Homebrew...")
        subprocess.run(['brew', 'install', 'ollama'], check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Homebrew not found, installing manually...")
    
    # Manual installation for macOS
    try:
        # Download Ollama for macOS
        url = "https://ollama.com/download/ollama-darwin"
        local_path = "/tmp/ollama"
        
        print(f"📥 Downloading Ollama from {url}...")
        urllib.request.urlretrieve(url, local_path)
        
        # Make executable and move to /usr/local/bin
        os.chmod(local_path, 0o755)
        
        # Try to move to /usr/local/bin (may require sudo)
        try:
            subprocess.run(['sudo', 'mv', local_path, '/usr/local/bin/ollama'], check=True)
            print("✅ Ollama installed to /usr/local/bin/ollama")
            return True
        except subprocess.CalledProcessError:
            # Fallback to user's local bin
            user_bin = Path.home() / '.local' / 'bin'
            user_bin.mkdir(parents=True, exist_ok=True)
            subprocess.run(['mv', local_path, str(user_bin / 'ollama')], check=True)
            print(f"✅ Ollama installed to {user_bin / 'ollama'}")
            print(f"⚠️  Make sure {user_bin} is in your PATH")
            return True
            
    except Exception as e:
        print(f"❌ Failed to install Ollama: {e}")
        return False

def install_ollama_linux():
    """Install Ollama on Linux."""
    print("🐧 Installing Ollama for Linux...")
    
    try:
        # Use the official install script
        subprocess.run(['curl', '-fsSL', 'https://ollama.com/install.sh'], 
                      stdout=subprocess.PIPE, check=True)
        result = subprocess.run(['sh'], input=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Ollama: {e}")
        return False

def install_ollama_windows():
    """Install Ollama on Windows."""
    print("🪟 Installing Ollama for Windows...")
    print("Please download and install Ollama manually from:")
    print("https://ollama.com/download/windows")
    print("After installation, restart your terminal and run this script again.")
    return False

def check_ollama_installation():
    """Check if Ollama is properly installed."""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Ollama is installed: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def start_ollama_service():
    """Start the Ollama service."""
    system, _ = get_system_info()
    
    try:
        if system == 'darwin':
            # On macOS, start as background service
            print("🚀 Starting Ollama service...")
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        elif system == 'linux':
            # On Linux, try systemd first, then manual
            try:
                subprocess.run(['sudo', 'systemctl', 'start', 'ollama'], check=True)
                subprocess.run(['sudo', 'systemctl', 'enable', 'ollama'], check=True)
                print("✅ Ollama service started via systemd")
            except subprocess.CalledProcessError:
                print("🚀 Starting Ollama service manually...")
                subprocess.Popen(['ollama', 'serve'],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
        
        # Wait a moment for service to start
        import time
        time.sleep(3)
        
        # Test connection
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama service is running")
            return True
        else:
            print("⚠️  Ollama service may not be running properly")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start Ollama service: {e}")
        return False

def download_recommended_models():
    """Download recommended models for the AI system."""
    models = [
        'llama3.2:3b',  # Fast, good for general queries
        'mistral:7b',   # Good balance of speed and capability
    ]
    
    print("📦 Downloading recommended models...")
    
    for model in models:
        try:
            print(f"⬇️  Downloading {model}...")
            result = subprocess.run(['ollama', 'pull', model], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {model} downloaded successfully")
            else:
                print(f"⚠️  Failed to download {model}: {result.stderr}")
        except Exception as e:
            print(f"❌ Error downloading {model}: {e}")

def main():
    """Main installation function."""
    print("🤖 Ollama Installation Script")
    print("=" * 50)
    
    # Check if already installed
    if check_ollama_installation():
        print("✅ Ollama is already installed!")
        
        # Start service if not running
        try:
            subprocess.run(['ollama', 'list'], 
                          capture_output=True, check=True)
            print("✅ Ollama service is running")
        except subprocess.CalledProcessError:
            print("🚀 Starting Ollama service...")
            start_ollama_service()
        
        # Download models
        download_recommended_models()
        return True
    
    # Install based on platform
    system, arch = get_system_info()
    print(f"🖥️  Detected system: {system} ({arch})")
    
    success = False
    if system == 'darwin':
        success = install_ollama_macos()
    elif system == 'linux':
        success = install_ollama_linux()
    elif system == 'windows':
        success = install_ollama_windows()
    else:
        print(f"❌ Unsupported platform: {system}")
        return False
    
    if not success:
        print("❌ Installation failed")
        return False
    
    # Verify installation
    if not check_ollama_installation():
        print("❌ Installation verification failed")
        return False
    
    # Start service
    if not start_ollama_service():
        print("⚠️  Service start failed, but installation succeeded")
    
    # Download models
    download_recommended_models()
    
    print("\n🎉 Ollama installation completed!")
    print("You can now use Ollama with the AI Employee Decision System")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)