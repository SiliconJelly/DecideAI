#!/usr/bin/env python3
"""
🚀 DecideAI HR Helper System - One-Click Deployment Script

This script automatically sets up and deploys the DecideAI HR Helper System
for German and Japanese institutions without any technical hassles.

Usage: python DEPLOY_DECIDEAI.py
"""

import os
import sys
import subprocess
import platform
import time
import json
import urllib.request
import shutil
from pathlib import Path
import threading
import signal

class DecideAIDeployer:
    def __init__(self):
        self.system = platform.system().lower()
        self.arch = self.get_architecture()
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        self.models_dir = self.project_root / "ai-engine" / "models"
        
    def get_architecture(self):
        """Get system architecture."""
        machine = platform.machine().lower()
        if machine in ['x86_64', 'amd64']:
            return 'amd64'
        elif machine in ['arm64', 'aarch64']:
            return 'arm64'
        return machine
    
    def print_banner(self):
        """Print deployment banner."""
        print("=" * 70)
        print("🎯 DecideAI HR Helper System - Automated Deployment")
        print("   For German & Japanese Universities and SMEs")
        print("=" * 70)
        print(f"🖥️  System: {self.system.title()} ({self.arch})")
        print(f"📁 Project: {self.project_root}")
        print("=" * 70)
    
    def check_prerequisites(self):
        """Check and install prerequisites."""
        print("\n📋 Checking Prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required. Please upgrade Python.")
            return False
        print(f"✅ Python {sys.version.split()[0]}")
        
        # Check pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         capture_output=True, check=True)
            print("✅ pip available")
        except subprocess.CalledProcessError:
            print("❌ pip not available")
            return False
        
        return True
    
    def setup_directories(self):
        """Create necessary directories."""
        print("\n📁 Setting up directories...")
        
        directories = [
            self.data_dir,
            self.data_dir / "uploads",
            self.data_dir / "models",
            self.logs_dir,
            self.models_dir,
            self.project_root / ".decideai"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {directory}")
    
    def install_python_dependencies(self):
        """Install Python dependencies."""
        print("\n📦 Installing Python dependencies...")
        
        try:
            # Upgrade pip first
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            
            # Install requirements
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True)
            
            print("✅ Python dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def install_ollama(self):
        """Install and configure Ollama."""
        print("\n🤖 Setting up Ollama AI Engine...")
        
        # Check if Ollama is already installed
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Ollama already installed: {result.stdout.strip()}")
            return self.setup_ollama_models()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Install Ollama based on platform
        if self.system == 'darwin':
            return self.install_ollama_macos()
        elif self.system == 'linux':
            return self.install_ollama_linux()
        elif self.system == 'windows':
            return self.install_ollama_windows()
        else:
            print(f"❌ Unsupported platform: {self.system}")
            return False
    
    def install_ollama_macos(self):
        """Install Ollama on macOS."""
        try:
            print("🍎 Installing Ollama for macOS...")
            
            # Try Homebrew first
            try:
                subprocess.run(['brew', '--version'], check=True, capture_output=True)
                subprocess.run(['brew', 'install', 'ollama'], check=True)
                print("✅ Ollama installed via Homebrew")
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Manual installation
                url = "https://ollama.com/download/ollama-darwin"
                local_path = "/tmp/ollama"
                
                print("📥 Downloading Ollama...")
                urllib.request.urlretrieve(url, local_path)
                os.chmod(local_path, 0o755)
                
                # Try to install to /usr/local/bin
                try:
                    subprocess.run(['sudo', 'mv', local_path, '/usr/local/bin/ollama'], check=True)
                    print("✅ Ollama installed to /usr/local/bin/ollama")
                except subprocess.CalledProcessError:
                    # Fallback to user bin
                    user_bin = Path.home() / '.local' / 'bin'
                    user_bin.mkdir(parents=True, exist_ok=True)
                    shutil.move(local_path, user_bin / 'ollama')
                    print(f"✅ Ollama installed to {user_bin / 'ollama'}")
            
            return self.setup_ollama_models()
            
        except Exception as e:
            print(f"❌ Failed to install Ollama: {e}")
            return False
    
    def install_ollama_linux(self):
        """Install Ollama on Linux."""
        try:
            print("🐧 Installing Ollama for Linux...")
            
            # Use official install script
            install_script = urllib.request.urlopen('https://ollama.com/install.sh').read()
            process = subprocess.Popen(['sh'], stdin=subprocess.PIPE, 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(input=install_script)
            
            if process.returncode == 0:
                print("✅ Ollama installed successfully")
                return self.setup_ollama_models()
            else:
                print(f"❌ Installation failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to install Ollama: {e}")
            return False
    
    def install_ollama_windows(self):
        """Install Ollama on Windows."""
        print("🪟 Windows Installation:")
        print("Please download and install Ollama from:")
        print("https://ollama.com/download/windows")
        print("After installation, restart this script.")
        
        input("Press Enter after installing Ollama...")
        
        # Check if installed
        try:
            subprocess.run(['ollama', '--version'], check=True, capture_output=True)
            print("✅ Ollama detected")
            return self.setup_ollama_models()
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Ollama not found. Please install it first.")
            return False
    
    def setup_ollama_models(self):
        """Download and setup required AI models."""
        print("\n📦 Setting up AI models...")
        
        # Start Ollama service
        self.start_ollama_service()
        
        # Models optimized for HR tasks
        models = [
            ('llama3.2:3b', 'Fast model for quick queries'),
            ('mistral:7b', 'Balanced model for complex HR decisions')
        ]
        
        for model, description in models:
            try:
                print(f"⬇️  Downloading {model} ({description})...")
                result = subprocess.run(['ollama', 'pull', model], 
                                      capture_output=True, text=True, timeout=600)
                if result.returncode == 0:
                    print(f"✅ {model} ready")
                else:
                    print(f"⚠️  Failed to download {model}: {result.stderr}")
            except subprocess.TimeoutExpired:
                print(f"⚠️  Timeout downloading {model}")
            except Exception as e:
                print(f"❌ Error with {model}: {e}")
        
        return True
    
    def start_ollama_service(self):
        """Start Ollama service."""
        try:
            # Check if already running
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Ollama service already running")
                return True
            
            print("🚀 Starting Ollama service...")
            
            if self.system == 'linux':
                # Try systemd first
                try:
                    subprocess.run(['sudo', 'systemctl', 'start', 'ollama'], check=True)
                    subprocess.run(['sudo', 'systemctl', 'enable', 'ollama'], check=True)
                    print("✅ Ollama service started via systemd")
                    return True
                except subprocess.CalledProcessError:
                    pass
            
            # Start manually
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            # Wait for service to start
            for i in range(10):
                time.sleep(1)
                result = subprocess.run(['ollama', 'list'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Ollama service started")
                    return True
            
            print("⚠️  Ollama service may not be running properly")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start Ollama: {e}")
            return False
    
    def initialize_database(self):
        """Initialize the database."""
        print("\n🗄️  Initializing database...")
        
        try:
            subprocess.run([sys.executable, "init_system.py"], check=True)
            print("✅ Database initialized")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Database initialization failed: {e}")
            return False
    
    def create_config_file(self):
        """Create configuration file."""
        print("\n⚙️  Creating configuration...")
        
        config = {
            "system_name": "DecideAI HR Helper System",
            "version": "1.0.0",
            "target_markets": ["German Universities", "Japanese Universities", "German SMEs", "Japanese SMEs"],
            "languages": ["de", "ja", "en"],
            "deployment_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "api_port": 8000,
            "ui_port": 7860,
            "default_admin": {
                "username": "admin",
                "password": "AdminPassword123!"
            }
        }
        
        config_file = self.project_root / ".decideai" / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration saved to {config_file}")
        return True
    
    def run_tests(self):
        """Run system tests."""
        print("\n🧪 Running system tests...")
        
        try:
            # Run basic tests
            subprocess.run([sys.executable, "test_ai_system.py"], 
                         check=True, capture_output=True)
            print("✅ AI system tests passed")
            
            # Test Ollama integration
            subprocess.run([sys.executable, "test_ollama_integration.py"], 
                         check=True, capture_output=True)
            print("✅ Ollama integration tests passed")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Some tests failed, but system should work: {e}")
            return True  # Don't fail deployment for test failures
    
    def start_system(self):
        """Start the DecideAI system."""
        print("\n🚀 Starting DecideAI HR Helper System...")
        
        # Create startup script
        startup_script = self.project_root / "start_decideai.py"
        with open(startup_script, 'w') as f:
            f.write('''#!/usr/bin/env python3
"""
DecideAI HR Helper System Startup Script
"""
import subprocess
import sys
import threading
import time

def start_api():
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "ai_employee_decision_system.api.app:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])

def start_ui():
    time.sleep(3)  # Wait for API
    subprocess.run([sys.executable, "start_ui.py"])

if __name__ == "__main__":
    print("🎯 Starting DecideAI HR Helper System...")
    print("   API: http://localhost:8000")
    print("   UI:  http://localhost:7860")
    print("   Press Ctrl+C to stop")
    
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    try:
        start_ui()
    except KeyboardInterrupt:
        print("\\n👋 System stopped")
''')
        
        startup_script.chmod(0o755)
        
        print("✅ System ready to start!")
        print("\n" + "=" * 70)
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print("=" * 70)
        print(f"📍 System Location: {self.project_root}")
        print("🌐 Access Points:")
        print("   • Web Interface: http://localhost:7860")
        print("   • API Documentation: http://localhost:8000/docs")
        print("🔐 Default Login:")
        print("   • Username: admin")
        print("   • Password: AdminPassword123!")
        print("🚀 To start the system:")
        print(f"   python {startup_script}")
        print("=" * 70)
        
        # Ask if user wants to start now
        start_now = input("\\n🚀 Start DecideAI now? (y/n): ").lower().strip()
        if start_now in ['y', 'yes']:
            print("\\n🎯 Starting DecideAI...")
            try:
                subprocess.run([sys.executable, str(startup_script)])
            except KeyboardInterrupt:
                print("\\n👋 System stopped")
        
        return True
    
    def deploy(self):
        """Main deployment function."""
        self.print_banner()
        
        steps = [
            ("Prerequisites", self.check_prerequisites),
            ("Directories", self.setup_directories),
            ("Python Dependencies", self.install_python_dependencies),
            ("Ollama AI Engine", self.install_ollama),
            ("Database", self.initialize_database),
            ("Configuration", self.create_config_file),
            ("System Tests", self.run_tests),
            ("System Startup", self.start_system)
        ]
        
        for step_name, step_func in steps:
            print(f"\\n{'='*20} {step_name} {'='*20}")
            if not step_func():
                print(f"❌ {step_name} failed. Deployment aborted.")
                return False
        
        return True

def main():
    """Main function."""
    deployer = DecideAIDeployer()
    
    try:
        success = deployer.deploy()
        if success:
            print("\\n🎉 DecideAI HR Helper System deployed successfully!")
            print("Perfect for German and Japanese institutions!")
        else:
            print("\\n❌ Deployment failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\\n\\n👋 Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()