from __future__ import annotations
import time
from datetime import datetime
from typing import Dict, Any, TypedDict

class EndpointDict(TypedDict, total=False):
    url: str
    method: str
    parameters: Dict[str, Any]
    description: str

class ServiceDict(TypedDict):
    service_id: str
    name: str
    description: str
    endpoints: Dict[str, EndpointDict]
    status: str
    timestamp: int
    last_updated: str

class Service:
    def __init__(
        self, 
        service_id: str, 
        name: str, 
        description: str, 
        endpoints: Dict[str, Any], 
        status: str = "active"
    ):
        self.service_id: str = service_id
        self.name: str = name
        self.description: str = description
        self.endpoints: Dict[str, Any] = endpoints
        self.status: str = status
        self.timestamp: int = int(time.time())
        self.last_updated: str = datetime.now().isoformat()

    def to_dict(self) -> ServiceDict:
        """Convert service object to dictionary representation."""
        return {
            "service_id": self.service_id,
            "name": self.name,
            "description": self.description,
            "endpoints": self.endpoints,
            "status": self.status,
            "timestamp": self.timestamp,
            "last_updated": self.last_updated
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Service:
        """Create a Service instance from a dictionary."""
        service = cls(
            service_id=data.get("service_id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            endpoints=data.get("endpoints", {}),
            status=data.get("status", "active")
        )
        service.timestamp = data.get("timestamp", int(time.time()))
        service.last_updated = data.get("last_updated", datetime.now().isoformat())
        return service