import json
from typing import Dict, Any, Optional, Union, List, cast

import cherrypy
from services.registry_service import RegistryService

class CatalogController:
    def __init__(self):
        self.registry_service = RegistryService()

    @cherrypy.expose
    def index(self) -> str:
        """Root endpoint that returns basic API information."""
        return "Resource Catalog API is running. Use the documented endpoints to interact with the catalog."

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def services(self) -> Dict[str, Any]:
        """Get all registered services."""
        return self.registry_service.get_all_services()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def service(self, service_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific service by ID."""
        if service_id:
            result = self.registry_service.get_service(service_id)
            if result:
                return result
            else:
                cherrypy.response.status = 404
                return {"error": f"Service with ID {service_id} not found"}
        else:
            cherrypy.response.status = 400
            return {"error": "Service ID is required"}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def register_service(self) -> Dict[str, Any]:
        """Register a new service."""
        try:
            data = cherrypy.request.json
        except (AttributeError, ValueError):
            cherrypy.response.status = 400
            return {"error": "Invalid JSON data"}
        
        if not data:
            cherrypy.response.status = 400
            return {"error": "No data provided"}
        
        try:
            result = self.registry_service.register_service(data)
            return result
        except Exception as e:
            cherrypy.response.status = 400
            return {"error": str(e)}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update_service(self, service_id: str) -> Dict[str, Any]:
        """Update an existing service."""
        try:
            data = cherrypy.request.json
        except (AttributeError, ValueError):
            cherrypy.response.status = 400
            return {"error": "Invalid JSON data"}
        
        if not data:
            cherrypy.response.status = 400
            return {"error": "No data provided"}
        
        try:
            result = self.registry_service.update_service(service_id, data)
            if result:
                return result
            else:
                cherrypy.response.status = 404
                return {"error": f"Service with ID {service_id} not found"}
        except Exception as e:
            cherrypy.response.status = 400
            return {"error": str(e)}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def delete_service(self, service_id: str) -> Dict[str, Any]:
        """Delete a service."""
        try:
            result = self.registry_service.delete_service(service_id)
            if result:
                return {"success": True, "message": f"Service {service_id} deleted"}
            else:
                cherrypy.response.status = 404
                return {"error": f"Service with ID {service_id} not found"}
        except Exception as e:
            cherrypy.response.status = 400
            return {"error": str(e)}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def devices(self, device_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all devices, optionally filtered by type."""
        if device_type:
            return self.registry_service.get_devices_by_type(device_type)
        else:
            return self.registry_service.get_all_devices()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def device(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific device by ID."""
        if device_id:
            result = self.registry_service.get_device(device_id)
            if result:
                return result
            else:
                cherrypy.response.status = 404
                return {"error": f"Device with ID {device_id} not found"}
        else:
            cherrypy.response.status = 400
            return {"error": "Device ID is required"}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def register_device(self) -> Dict[str, Any]:
        """Register a new device."""
        try:
            data = cherrypy.request.json
        except (AttributeError, ValueError):
            cherrypy.response.status = 400
            return {"error": "Invalid JSON data"}
        
        if not data:
            cherrypy.response.status = 400
            return {"error": "No data provided"}
        
        try:
            result = self.registry_service.register_device(data)
            return result
        except Exception as e:
            cherrypy.response.status = 400
            return {"error": str(e)}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update_device(self, device_id: str) -> Dict[str, Any]:
        """Update an existing device."""
        try:
            data = cherrypy.request.json
        except (AttributeError, ValueError):
            cherrypy.response.status = 400
            return {"error": "Invalid JSON data"}
        
        if not data:
            cherrypy.response.status = 400
            return {"error": "No data provided"}
        
        try:
            result = self.registry_service.update_device(device_id, data)
            if result:
                return result
            else:
                cherrypy.response.status = 404
                return {"error": f"Device with ID {device_id} not found"}
        except Exception as e:
            cherrypy.response.status = 400
            return {"error": str(e)}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update_device_measurements(self, device_id: str) -> Dict[str, Any]:
        """Update measurements for a device."""
        try:
            data = cherrypy.request.json
        except (AttributeError, ValueError):
            cherrypy.response.status = 400
            return {"error": "Invalid JSON data"}
        
        if not data:
            cherrypy.response.status = 400
            return {"error": "No data provided"}
        
        try:
            result = self.registry_service.update_device_measurements(device_id, data)
            if result:
                return result
            else:
                cherrypy.response.status = 404
                return {"error": f"Device with ID {device_id} not found"}
        except Exception as e:
            cherrypy.response.status = 400
            return {"error": str(e)}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update_device_status(self, device_id: str) -> Dict[str, Any]:
        """Update status for a device."""
        try:
            data = cherrypy.request.json
        except (AttributeError, ValueError):
            cherrypy.response.status = 400
            return {"error": "Invalid JSON data"}
        
        if not data or "status" not in data:
            cherrypy.response.status = 400
            return {"error": "Status information is required"}
        
        try:
            result = self.registry_service.update_device_status(device_id, data["status"])
            if result:
                return result
            else:
                cherrypy.response.status = 404
                return {"error": f"Device with ID {device_id} not found"}
        except Exception as e:
            cherrypy.response.status = 400
            return {"error": str(e)}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def delete_device(self, device_id: str) -> Dict[str, Any]:
        """Delete a device."""
        try:
            result = self.registry_service.delete_device(device_id)
            if result:
                return {"success": True, "message": f"Device {device_id} deleted"}
            else:
                cherrypy.response.status = 404
                return {"error": f"Device with ID {device_id} not found"}
        except Exception as e:
            cherrypy.response.status = 400
            return {"error": str(e)}