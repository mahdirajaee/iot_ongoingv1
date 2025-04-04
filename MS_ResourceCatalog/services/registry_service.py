import json
import os
import time
from datetime import datetime
import threading
from typing import Dict, List, Optional, Any, Union, cast

from models.service import Service, ServiceDict
from models.device import Device, DeviceDict

class RegistryService:
    def __init__(self, storage_file: str = 'registry_data.json'):
        self.storage_file: str = storage_file
        self.services: Dict[str, Service] = {}
        self.devices: Dict[str, Device] = {}
        self.last_updated: str = datetime.now().isoformat()
        
        self.lock = threading.Lock()
        
        self.load_data()
        
        self.start_cleanup_timer()

    def load_data(self) -> None:
        """Load registry data from storage file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    
                    services_data = data.get('services', {})
                    for service_id, service_data in services_data.items():
                        self.services[service_id] = Service.from_dict(service_data)
                    
                    devices_data = data.get('devices', {})
                    for device_id, device_data in devices_data.items():
                        self.devices[device_id] = Device.from_dict(device_data)
                    
                    self.last_updated = data.get('last_updated', datetime.now().isoformat())
            except Exception as e:
                print(f"Error loading registry data: {e}")
                self.services = {}
                self.devices = {}
                self.last_updated = datetime.now().isoformat()
        else:
            self.services = {}
            self.devices = {}
            self.last_updated = datetime.now().isoformat()

    def save_data(self) -> None:
        """Save registry data to storage file."""
        with self.lock:
            data = {
                'services': {service_id: service.to_dict() for service_id, service in self.services.items()},
                'devices': {device_id: device.to_dict() for device_id, device in self.devices.items()},
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.last_updated = datetime.now().isoformat()

    def start_cleanup_timer(self) -> None:
        """Start background thread for cleaning up stale entries."""
        cleanup_thread = threading.Thread(target=self._cleanup_timer)
        cleanup_thread.daemon = True
        cleanup_thread.start()

    def _cleanup_timer(self) -> None:
        """Timer function for periodic cleanup of stale entries."""
        while True:
            time.sleep(300)  # Check every 5 minutes
            self._cleanup_stale_entries()

    def _cleanup_stale_entries(self) -> None:
        """Remove or mark inactive services and devices that haven't been updated within timeout period."""
        current_time = int(time.time())
        
        with self.lock:
            services_to_remove: List[str] = []
            for service_id, service in self.services.items():
                if current_time - service.timestamp > 900:  # 15 minutes timeout
                    services_to_remove.append(service_id)
            
            for service_id in services_to_remove:
                del self.services[service_id]
            
            for device_id, device in self.devices.items():
                if current_time - device.timestamp > 900:  # 15 minutes timeout
                    device.status = "inactive"
            
            if services_to_remove:
                self.save_data()

    def register_service(self, service_data: Dict[str, Any]) -> ServiceDict:
        """Register a new service in the catalog."""
        with self.lock:
            service = Service.from_dict(service_data)
            self.services[service.service_id] = service
            self.save_data()
            return service.to_dict()

    def update_service(self, service_id: str, service_data: Dict[str, Any]) -> Optional[ServiceDict]:
        """Update an existing service in the catalog."""
        with self.lock:
            if service_id not in self.services:
                return None
            
            service = Service.from_dict(service_data)
            service.service_id = service_id
            self.services[service_id] = service
            self.save_data()
            return service.to_dict()

    def get_service(self, service_id: str) -> Optional[ServiceDict]:
        """Get a service by its ID."""
        with self.lock:
            service = self.services.get(service_id)
            if service:
                return service.to_dict()
            return None

    def get_all_services(self) -> Dict[str, ServiceDict]:
        """Get all registered services."""
        with self.lock:
            return {service_id: service.to_dict() for service_id, service in self.services.items()}

    def delete_service(self, service_id: str) -> bool:
        """Delete a service by its ID."""
        with self.lock:
            if service_id in self.services:
                del self.services[service_id]
                self.save_data()
                return True
            return False

    def register_device(self, device_data: Dict[str, Any]) -> DeviceDict:
        """Register a new device in the catalog."""
        with self.lock:
            device = Device.from_dict(device_data)
            self.devices[device.device_id] = device
            self.save_data()
            return device.to_dict()

    def update_device(self, device_id: str, device_data: Dict[str, Any]) -> Optional[DeviceDict]:
        """Update an existing device in the catalog."""
        with self.lock:
            if device_id not in self.devices:
                return None
            
            device = Device.from_dict(device_data)
            device.device_id = device_id
            self.devices[device_id] = device
            self.save_data()
            return device.to_dict()

    def update_device_measurements(self, device_id: str, measurements: Dict[str, Any]) -> Optional[DeviceDict]:
        """Update measurements for a device."""
        with self.lock:
            if device_id not in self.devices:
                return None
            
            device = self.devices[device_id]
            device.update_measurements(measurements)
            self.save_data()
            return device.to_dict()

    def update_device_status(self, device_id: str, status: str) -> Optional[DeviceDict]:
        """Update status for a device."""
        with self.lock:
            if device_id not in self.devices:
                return None
            
            device = self.devices[device_id]
            device.update_status(status)
            self.save_data()
            return device.to_dict()

    def get_device(self, device_id: str) -> Optional[DeviceDict]:
        """Get a device by its ID."""
        with self.lock:
            device = self.devices.get(device_id)
            if device:
                return device.to_dict()
            return None

    def get_all_devices(self) -> Dict[str, DeviceDict]:
        """Get all registered devices."""
        with self.lock:
            return {device_id: device.to_dict() for device_id, device in self.devices.items()}

    def get_devices_by_type(self, device_type: str) -> Dict[str, DeviceDict]:
        """Get devices filtered by type."""
        with self.lock:
            return {device_id: device.to_dict() for device_id, device in self.devices.items() 
                    if device.device_type == device_type}

    def delete_device(self, device_id: str) -> bool:
        """Delete a device by its ID."""
        with self.lock:
            if device_id in self.devices:
                del self.devices[device_id]
                self.save_data()
                return True
            return False