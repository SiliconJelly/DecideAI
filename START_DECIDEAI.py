#!/usr/bin/env python3
"""
🚀 DecideAI HR Helper System - Unified Service Orchestration

Production-ready startup with proper service management, dependency handling,
and health monitoring for German and Japanese institutions.

Usage: python START_DECIDEAI.py
"""

import os
import sys
import time
import webbrowser
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_employee_decision_system.services.service_orchestration import (
    ServiceManager, get_default_service_configs, ServiceState
)

class DecideAIOrchestrator:
    """Main DecideAI application orchestrator."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.service_manager = ServiceManager()
        self.setup_services()
        
    def setup_services(self):
        """Setup service configurations."""
        # Register default services
        for config in get_default_service_configs():
            self.service_manager.register_service(config)
    
    def print_banner(self):
        """Print startup banner."""
        print("=" * 70)
        print("🎯 DecideAI HR Helper System")
        print("   AI-Powered HR Support for German & Japanese Institutions")
        print("=" * 70)
        print("🏛️  Perfect for:")
        print("   • German Universities & Research Institutes")
        print("   • Japanese Universities & Academic Centers") 
        print("   • German SMEs & Mittelstand Companies")
        print("   • Japanese SMEs & Technology Companies")
        print("=" * 70)
    
    def check_prerequisites(self):
        """Check system prerequisites."""
        print("🔍 Checking system prerequisites...")
        
        # Check database
        db_path = self.project_root / "data" / "employee_system.db"
        if not db_path.exists():
            print("⚠️  Database not found. Initializing...")
            try:
                import subprocess
                subprocess.run([sys.executable, "init_system.py"], check=True)
                print("✅ Database initialized")
            except subprocess.CalledProcessError:
                print("❌ Database initialization failed")
                return False
        else:
            print("✅ Database ready")
        
        # Check Ollama
        try:
            import subprocess
            subprocess.run(['ollama', '--version'], 
                         capture_output=True, check=True)
            print("✅ Ollama AI engine available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Ollama not found. Please run DEPLOY_DECIDEAI.py first")
            return False
        
        # Create logs directory
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        print("✅ System prerequisites satisfied")
        return True
    
    def start_services_with_progress(self):
        """Start services with progress indication."""
        print("\n🚀 Starting DecideAI services...")
        print("   Services will start in dependency order: Ollama → API → UI")
        print()
        
        # Start all services
        success = self.service_manager.start_all_services()
        
        if not success:
            print("\n❌ Failed to start services")
            return False
        
        # Wait for system to be fully ready
        print("⏳ Waiting for all services to be ready...")
        
        max_wait = 120  # 2 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if self.service_manager.is_system_ready():
                print("✅ All services are ready!")
                return True
            
            # Show progress
            status = self.service_manager.get_system_status()
            ready_count = sum(1 for s in status.values() 
                            if s.state == ServiceState.RUNNING and s.health.is_healthy)
            total_count = len(status)
            
            print(f"   Progress: {ready_count}/{total_count} services ready", end="\r")
            time.sleep(2)
        
        print("\n⚠️  Services started but may not be fully ready")
        return True
    
    def show_service_status(self):
        """Show detailed service status."""
        print("\n📊 Service Status:")
        print("-" * 50)
        
        status = self.service_manager.get_system_status()
        
        for service_name, service_status in status.items():
            state_emoji = {
                ServiceState.RUNNING: "🟢",
                ServiceState.STARTING: "🟡",
                ServiceState.STOPPED: "🔴",
                ServiceState.FAILED: "❌"
            }.get(service_status.state, "⚪")
            
            health_emoji = "💚" if service_status.health.is_healthy else "💔"
            
            print(f"{state_emoji} {service_name.upper()}: {service_status.state.value}")
            if service_status.port:
                print(f"   Port: {service_status.port}")
            if service_status.pid:
                print(f"   PID: {service_status.pid}")
            if service_status.health.last_check:
                print(f"   Health: {health_emoji} (checked {service_status.health.last_check.strftime('%H:%M:%S')})")
            if service_status.uptime.total_seconds() > 0:
                uptime_str = str(service_status.uptime).split('.')[0]  # Remove microseconds
                print(f"   Uptime: {uptime_str}")
            print()
    
    def open_browser(self):
        """Open web browser to the application."""
        print("🌍 Opening web browser...")
        try:
            webbrowser.open("http://localhost:7860")
            print("✅ Browser opened to DecideAI interface")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print("   Please manually open: http://localhost:7860")
    
    def show_access_info(self):
        """Show access information."""
        print("\n" + "=" * 70)
        print("🎉 DecideAI HR Helper System is RUNNING!")
        print("=" * 70)
        print("🌐 Access Points:")
        print("   • Web Interface:     http://localhost:7860")
        print("   • API Documentation: http://localhost:8000/docs")
        print("   • API Health Check:  http://localhost:8000/health")
        print("   • Ollama AI:         http://localhost:11434")
        print()
        print("🔐 Default Login Credentials:")
        print("   • Username: admin")
        print("   • Password: AdminPassword123!")
        print()
        print("📊 Sample Data:")
        print("   • Upload sample_employees.csv to get started")
        print("   • Includes German and Japanese institutional data")
        print()
        print("🗣️  Try These Queries:")
        print("   • English: 'Who are our employees?'")
        print("   • German:  'Welche Professoren haben KI-Expertise?'")
        print("   • Japanese: '機械学習の経験がある従業員は誰ですか？'")
        print()
        print("⚠️  To stop the system: Press Ctrl+C")
        print("=" * 70)
    
    def run_interactive_mode(self):
        """Run in interactive mode with status updates."""
        try:
            while True:
                time.sleep(30)  # Update every 30 seconds
                
                # Check if all services are still running
                if not self.service_manager.is_system_ready():
                    print("\n⚠️  Service health issue detected")
                    self.show_service_status()
                
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down DecideAI...")
            self.service_manager.stop_all_services()
            print("✅ All services stopped gracefully")
    
    def start(self):
        """Start the DecideAI system."""
        self.print_banner()
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("\n❌ Prerequisites not met. Please run DEPLOY_DECIDEAI.py first.")
            return False
        
        # Start services
        if not self.start_services_with_progress():
            print("\n❌ Failed to start services")
            return False
        
        # Show status
        self.show_service_status()
        
        # Open browser
        self.open_browser()
        
        # Show access information
        self.show_access_info()
        
        # Run interactive mode
        self.run_interactive_mode()
        
        return True

def main():
    """Main function."""
    orchestrator = DecideAIOrchestrator()
    
    try:
        success = orchestrator.start()
        if not success:
            print("\n❌ Failed to start DecideAI")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()