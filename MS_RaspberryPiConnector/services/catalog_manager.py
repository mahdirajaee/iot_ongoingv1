import requests
import json
import os
import logging
import time
import socket

class CatalogManager:
    def __init__(self):
        self.service_name = os.getenv("SERVICE_NAME", "RaspberryPiConnector")
        self.service_port = int(os.getenv("SERVICE_PORT", 8081))
        self.catalog_url = os.getenv("CATALOG_URL", "http://localhost:8080")
        self.registration_endpoint = os.getenv("CATALOG_REGISTRATION_ENDPOINT", "/api/catalog/register")
        self.config_endpoint = os.getenv("CATALOG_GET_CONFIG_ENDPOINT", "/api/catalog/config")
        self.service_id = None

    def register_service(self):
        try:
            ip_address = self._get_ip_address()
            service_info = {
                "name": self.service_name,
                "ip": ip_address,
                "port": self.service_port,
                "endpoints": [
                    {
                        "path": "/api/sensors",
                        "method": "GET",
                        "description": "Get current sensor readings"
                    },
                    {
                        "path": "/api/actuator/valve",
                        "method": "POST",
                        "description": "Control valve state"
                    }
                ]
            }
            
            url = f"{self.catalog_url}{self.registration_endpoint}"
            response = requests.post(url, json=service_info)
            
            if response.status_code == 200:
                data = response.json()
                self.service_id = data.get("id")
                logging.info(f"Service registered successfully with ID: {self.service_id}")
                return True
            else:
                logging.error(f"Failed to register service: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logging.error(f"Error registering service: {e}")
            return False

    def get_configuration(self):
        try:
            url = f"{self.catalog_url}{self.config_endpoint}"
            params = {"service": self.service_name}
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                config = response.json()
                logging.info(f"Retrieved configuration from catalog: {config}")
                return config
            else:
                logging.warning(f"Failed to get configuration: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logging.error(f"Error getting configuration: {e}")
            return {}

    def update_sensor_status(self, status):
        try:
            if not self.service_id:
                logging.warning("Cannot update status: Service not registered")
                return False
                
            url = f"{self.catalog_url}/api/catalog/status/{self.service_id}/sensors"
            response = requests.put(url, json=status)
            
            if response.status_code != 200:
                logging.warning(f"Failed to update sensor status: {response.status_code} - {response.text}")
                return False
            return True
        except Exception as e:
            logging.error(f"Error updating sensor status: {e}")
            return False

    def update_actuator_status(self, status):
        try:
            if not self.service_id:
                logging.warning("Cannot update status: Service not registered")
                return False
                
            url = f"{self.catalog_url}/api/catalog/status/{self.service_id}/actuators"
            response = requests.put(url, json=status)
            
            if response.status_code != 200:
                logging.warning(f"Failed to update actuator status: {response.status_code} - {response.text}")
                return False
            return True
        except Exception as e:
            logging.error(f"Error updating actuator status: {e}")
            return False

    def _get_ip_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"