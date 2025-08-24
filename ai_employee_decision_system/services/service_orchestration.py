#!/usr/bin/env python3
"""
Service Orchestration System for DecideAI

Manages Ollama AI, API server, and UI server as a unified application
with proper dependency management, health monitoring, and cross-platform support.
"""

import os
import sys
import time
import signal
import subprocess
import threading
import webbrowser
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from pathlib import Path
import requests
import json
import logging
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/service_orchestration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ServiceState(Enum):
    """Service state enumeration."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAILED = "failed"
    UNKNOWN = "unknown"

class RestartPolicy(Enum):
    """Service restart policy."""
    NEVER = "never"
    ON_FAILURE = "on-failure"
    ALWAYS = "always"

@dataclass
class HealthStatus:
    """Health status information."""
    is_healthy: bool = False
    response_time: float = 0.0
    last_check: Optional[datetime] = None
    consecutive_failures: int = 0
    error_details: Optional[str] = None

@dataclass
class ServiceConfig:
    """Service configuration."""
    name: str
    command: List[str]
    port: Optional[int] = None
    host: str = "localhost"
    health_endpoint: Optional[str] = None
    startup_timeout: int = 60
    dependencies: List[str] = field(default_factory=list)
    restart_policy: RestartPolicy = RestartPolicy.ON_FAILURE
    max_restart_attempts: int = 3
    environment: Dict[str, str] = field(default_factory=dict)
    working_directory: Optional[str] = None

@dataclass
class ServiceStatus:
    """Service status information."""
    name: str
    state: ServiceState = ServiceState.STOPPED
    pid: Optional[int] = None
    port: Optional[int] = None
    health: HealthStatus = field(default_factory=HealthStatus)
    uptime: timedelta = field(default_factory=lambda: timedelta(0))
    start_time: Optional[datetime] = None
    restart_count: int = 0
    error_message: Optional[str] = None

class ProcessManager:
    """Cross-platform process management."""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.system = platform.system().lower()
    
    def start_process(self, config: ServiceConfig) -> Optional[subprocess.Popen]:
        """Start a service process."""
        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(config.environment)
            
            # Set working directory
            cwd = config.working_directory or os.getcwd()
            
            # Start process
            process = subprocess.Popen(
                config.command,
                env=env,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL
            )
            
            self.processes[config.name] = process
            logger.info(f"Started process for {config.name} with PID {process.pid}")
            return process
            
        except Exception as e:
            logger.error(f"Failed to start process for {config.name}: {e}")
            return None
    
    def stop_process(self, service_name: str, timeout: int = 30) -> bool:
        """Stop a service process gracefully."""
        if service_name not in self.processes:
            return True
        
        process = self.processes[service_name]
        
        try:
            # Try graceful shutdown first
            if self.system == "windows":
                process.terminate()
            else:
                process.send_signal(signal.SIGTERM)
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=timeout)
                logger.info(f"Process {service_name} stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                process.kill()
                process.wait()
                logger.warning(f"Process {service_name} force killed")
            
            del self.processes[service_name]
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop process {service_name}: {e}")
            return False
    
    def is_process_running(self, service_name: str) -> bool:
        """Check if a process is running."""
        if service_name not in self.processes:
            return False
        
        process = self.processes[service_name]
        return process.poll() is None
    
    def get_process_pid(self, service_name: str) -> Optional[int]:
        """Get process PID."""
        if service_name not in self.processes:
            return None
        return self.processes[service_name].pid

class HealthMonitor:
    """Service health monitoring."""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.health_callbacks: List[Callable[[str, HealthStatus], None]] = []
    
    def start_monitoring(self):
        """Start health monitoring."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Health monitoring started")
    
    def stop_monitoring(self):
        """Stop health monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Health monitoring stopped")
    
    def register_health_callback(self, callback: Callable[[str, HealthStatus], None]):
        """Register a health status callback."""
        self.health_callbacks.append(callback)
    
    def check_service_health(self, config: ServiceConfig) -> HealthStatus:
        """Check health of a specific service."""
        if not config.health_endpoint or not config.port:
            # No health check available, assume healthy if process is running
            return HealthStatus(is_healthy=True, last_check=datetime.now())
        
        try:
            start_time = time.time()
            url = f"http://{config.host}:{config.port}{config.health_endpoint}"
            
            response = requests.get(url, timeout=5)
            response_time = time.time() - start_time
            
            is_healthy = response.status_code == 200
            
            return HealthStatus(
                is_healthy=is_healthy,
                response_time=response_time,
                last_check=datetime.now(),
                consecutive_failures=0 if is_healthy else 1,
                error_details=None if is_healthy else f"HTTP {response.status_code}"
            )
            
        except Exception as e:
            return HealthStatus(
                is_healthy=False,
                response_time=0.0,
                last_check=datetime.now(),
                consecutive_failures=1,
                error_details=str(e)
            )
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            # This will be called by ServiceManager
            time.sleep(self.check_interval)

class DependencyManager:
    """Service dependency management."""
    
    def __init__(self):
        self.dependency_graph: Dict[str, List[str]] = {}
    
    def add_dependency(self, service: str, dependency: str):
        """Add a dependency relationship."""
        if service not in self.dependency_graph:
            self.dependency_graph[service] = []
        self.dependency_graph[service].append(dependency)
    
    def get_startup_order(self, services: List[str]) -> List[str]:
        """Get the correct startup order based on dependencies."""
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(service: str):
            if service in temp_visited:
                raise ValueError(f"Circular dependency detected involving {service}")
            if service in visited:
                return
            
            temp_visited.add(service)
            
            # Visit dependencies first
            for dependency in self.dependency_graph.get(service, []):
                if dependency in services:
                    visit(dependency)
            
            temp_visited.remove(service)
            visited.add(service)
            order.append(service)
        
        for service in services:
            if service not in visited:
                visit(service)
        
        return order
    
    def wait_for_dependency(self, dependency_name: str, config: ServiceConfig, 
                          status_getter: Callable[[str], ServiceStatus], 
                          timeout: int = 60) -> bool:
        """Wait for a dependency to be ready."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = status_getter(dependency_name)
            
            if status.state == ServiceState.RUNNING and status.health.is_healthy:
                logger.info(f"Dependency {dependency_name} is ready")
                return True
            
            logger.debug(f"Waiting for dependency {dependency_name} (state: {status.state})")
            time.sleep(2)
        
        logger.error(f"Timeout waiting for dependency {dependency_name}")
        return False

class ServiceManager:
    """Main service orchestration manager."""
    
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.service_status: Dict[str, ServiceStatus] = {}
        self.process_manager = ProcessManager()
        self.health_monitor = HealthMonitor()
        self.dependency_manager = DependencyManager()
        
        # Register health callback
        self.health_monitor.register_health_callback(self._on_health_change)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def register_service(self, config: ServiceConfig):
        """Register a service configuration."""
        self.services[config.name] = config
        self.service_status[config.name] = ServiceStatus(name=config.name)
        
        # Register dependencies
        for dependency in config.dependencies:
            self.dependency_manager.add_dependency(config.name, dependency)
        
        logger.info(f"Registered service: {config.name}")
    
    def start_all_services(self) -> bool:
        """Start all registered services in dependency order."""
        logger.info("Starting all services...")
        
        try:
            # Get startup order
            service_names = list(self.services.keys())
            startup_order = self.dependency_manager.get_startup_order(service_names)
            
            logger.info(f"Service startup order: {startup_order}")
            
            # Start services in order
            for service_name in startup_order:
                if not self.start_service(service_name):
                    logger.error(f"Failed to start {service_name}, aborting startup")
                    return False
            
            # Start health monitoring
            self.health_monitor.start_monitoring()
            
            logger.info("All services started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start services: {e}")
            return False
    
    def start_service(self, service_name: str) -> bool:
        """Start a specific service."""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
        
        config = self.services[service_name]
        status = self.service_status[service_name]
        
        logger.info(f"Starting service: {service_name}")
        status.state = ServiceState.STARTING
        
        try:
            # Wait for dependencies
            for dependency in config.dependencies:
                if not self.dependency_manager.wait_for_dependency(
                    dependency, config, self.get_service_status, config.startup_timeout
                ):
                    status.state = ServiceState.FAILED
                    status.error_message = f"Dependency {dependency} not ready"
                    return False
            
            # Start the process
            process = self.process_manager.start_process(config)
            if not process:
                status.state = ServiceState.FAILED
                status.error_message = "Failed to start process"
                return False
            
            status.pid = process.pid
            status.port = config.port
            status.start_time = datetime.now()
            
            # Wait for service to be ready
            if not self._wait_for_service_ready(service_name, config.startup_timeout):
                status.state = ServiceState.FAILED
                status.error_message = "Service failed to become ready"
                return False
            
            status.state = ServiceState.RUNNING
            logger.info(f"Service {service_name} started successfully")
            return True
            
        except Exception as e:
            status.state = ServiceState.FAILED
            status.error_message = str(e)
            logger.error(f"Failed to start service {service_name}: {e}")
            return False
    
    def stop_all_services(self) -> bool:
        """Stop all services in reverse dependency order."""
        logger.info("Stopping all services...")
        
        # Stop health monitoring
        self.health_monitor.stop_monitoring()
        
        # Get reverse startup order
        service_names = list(self.services.keys())
        try:
            startup_order = self.dependency_manager.get_startup_order(service_names)
            shutdown_order = list(reversed(startup_order))
        except:
            shutdown_order = service_names
        
        success = True
        for service_name in shutdown_order:
            if not self.stop_service(service_name):
                success = False
        
        logger.info("All services stopped")
        return success
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service."""
        if service_name not in self.services:
            return True
        
        status = self.service_status[service_name]
        logger.info(f"Stopping service: {service_name}")
        
        status.state = ServiceState.STOPPING
        
        success = self.process_manager.stop_process(service_name)
        
        status.state = ServiceState.STOPPED
        status.pid = None
        status.start_time = None
        status.uptime = timedelta(0)
        
        return success
    
    def get_service_status(self, service_name: str) -> ServiceStatus:
        """Get status of a specific service."""
        if service_name not in self.service_status:
            return ServiceStatus(name=service_name, state=ServiceState.UNKNOWN)
        
        status = self.service_status[service_name]
        
        # Update uptime
        if status.start_time and status.state == ServiceState.RUNNING:
            status.uptime = datetime.now() - status.start_time
        
        return status
    
    def get_system_status(self) -> Dict[str, ServiceStatus]:
        """Get status of all services."""
        return {name: self.get_service_status(name) for name in self.services.keys()}
    
    def is_system_ready(self) -> bool:
        """Check if the entire system is ready."""
        for service_name in self.services.keys():
            status = self.get_service_status(service_name)
            if status.state != ServiceState.RUNNING or not status.health.is_healthy:
                return False
        return True
    
    def _wait_for_service_ready(self, service_name: str, timeout: int) -> bool:
        """Wait for a service to be ready."""
        config = self.services[service_name]
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check if process is still running
            if not self.process_manager.is_process_running(service_name):
                return False
            
            # Check health if available
            health = self.health_monitor.check_service_health(config)
            self.service_status[service_name].health = health
            
            if health.is_healthy:
                return True
            
            time.sleep(2)
        
        return False
    
    def _on_health_change(self, service_name: str, health: HealthStatus):
        """Handle health status changes."""
        if service_name in self.service_status:
            self.service_status[service_name].health = health
            
            # Handle failures
            if not health.is_healthy and health.consecutive_failures >= 3:
                self._handle_service_failure(service_name)
    
    def _handle_service_failure(self, service_name: str):
        """Handle service failure."""
        config = self.services[service_name]
        status = self.service_status[service_name]
        
        logger.warning(f"Service {service_name} failed, attempting restart")
        
        if (config.restart_policy == RestartPolicy.ALWAYS or 
            (config.restart_policy == RestartPolicy.ON_FAILURE and 
             status.restart_count < config.max_restart_attempts)):
            
            status.restart_count += 1
            self.stop_service(service_name)
            time.sleep(5)  # Wait before restart
            self.start_service(service_name)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop_all_services()
        sys.exit(0)

# Default service configurations for DecideAI
def get_default_service_configs() -> List[ServiceConfig]:
    """Get default service configurations for DecideAI."""
    return [
        ServiceConfig(
            name="ollama",
            command=["ollama", "serve"],
            port=11434,
            health_endpoint="/api/tags",
            startup_timeout=60,
            restart_policy=RestartPolicy.ALWAYS
        ),
        ServiceConfig(
            name="api",
            command=[sys.executable, "-m", "uvicorn", 
                    "ai_employee_decision_system.api.app:app", 
                    "--host", "0.0.0.0", "--port", "8000"],
            port=8000,
            health_endpoint="/health",
            startup_timeout=30,
            dependencies=["ollama"],
            restart_policy=RestartPolicy.ON_FAILURE
        ),
        ServiceConfig(
            name="ui",
            command=[sys.executable, "start_ui.py"],
            port=7860,
            health_endpoint="/",
            startup_timeout=30,
            dependencies=["api"],
            restart_policy=RestartPolicy.ON_FAILURE
        )
    ]