from __future__ import annotations
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, TypedDict, Union

class LocationDict(TypedDict, total=False):
    latitude: float
    longitude: float
    zone: str
    section: str

class MeasurementsDict(TypedDict, total=False):
    temperature: float
    pressure: float
    timestamp: str

class DeviceDict(TypedDict):
    device_id: str
    name: str
    device_type: str
    measurements: MeasurementsDict
    location: LocationDict
    status: str
    associated_services: List[str]
    timestamp: int
    last_updated: str

class Device:
    def __init__(
        self, 
        device_id: str, 
        name: str, 
        device_type: str, 
        measurements: Optional[Dict[str, Any]] = None, 
        location: Optional[Dict[str, Any]] = None, 
        status: str = "active", 
        associated_services: Optional[List[str]] = None
    ):
        self.device_id: str = device_id
        self.name: str = name
        self.device_type: str = device_type
        self.measurements: Dict[str, Any] = measurements or {}
        self.location: Dict[str, Any] = location or {}
        self.status: str = status
        self.associated_services: List[str] = associated_services or []
        self.timestamp: int = int(time.time())
        self.last_updated: str = datetime.now().isoformat()

    def to_dict(self) -> DeviceDict:
        """Convert device object to dictionary representation."""
        return {
            "device_id": self.device_id,
            "name": self.name,
            "device_type": self.device_type,
            "measurements": self.measurements,
            "location": self.location,
            "status": self.status,
            "associated_services": self.associated_services,
            "timestamp": self.timestamp,
            "last_updated": self.last_updated
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Device:
        """Create a Device instance from a dictionary."""
        device = cls(
            device_id=data.get("device_id", ""),
            name=data.get("name", ""),
            device_type=data.get("device_type", ""),
            measurements=data.get("measurements", {}),
            location=data.get("location", {}),
            status=data.get("status", "active"),
            associated_services=data.get("associated_services", [])
        )
        device.timestamp = data.get("timestamp", int(time.time()))
        device.last_updated = data.get("last_updated", datetime.now().isoformat())
        return device

    def update_measurements(self, measurements: Dict[str, Any]) -> None:
        """Update device measurements and timestamp."""
        self.measurements.update(measurements)
        self.last_updated = datetime.now().isoformat()
        self.timestamp = int(time.time())

    def update_status(self, status: str) -> None:
        """Update device status and timestamp."""
        self.status = status
        self.last_updated = datetime.now().isoformat()
        self.timestamp = int(time.time())