import logging
import requests
import json
import time
import threading
from datetime import datetime

class ControlService:
    def __init__(self, mqtt_handler, threshold_utils, catalog_url):
        self.mqtt_handler = mqtt_handler
        self.threshold_utils = threshold_utils
        self.catalog_url = catalog_url
        self.latest_data = {
            "temperature": None,
            "pressure": None,
            "timestamp": None
        }
        self.service_registered = False
        self.service_info = {
            "id": "control_center",
            "name": "Control Center",
            "endpoint": None,
            "port": None
        }
        
        self.register_thread = threading.Thread(target=self._periodic_registration)
        self.register_thread.daemon = True
        self.register_thread.start()
    
    def _periodic_registration(self):
        while True:
            self._register_with_catalog()
            time.sleep(60)
    
    def _register_with_catalog(self):
        try:
            response = requests.post(
                f"{self.catalog_url}/services", 
                json=self.service_info,
                timeout=5  # Add timeout to prevent long waits
            )
            
            if response.status_code == 200 or response.status_code == 201:
                logging.info("Successfully registered with the Resource Catalog")
                self.service_registered = True
            else:
                logging.warning(f"Failed to register with Resource Catalog: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            logging.warning("Resource Catalog not available - will retry later")
        except Exception as e:
            logging.warning(f"Error registering with Resource Catalog: {str(e)}")
    
    def update_service_info(self, host, port):
        self.service_info["endpoint"] = f"http://{host}:{port}"
        self.service_info["port"] = port
    
    def handle_sensor_data(self, topic, data):
        current_time = datetime.now().isoformat()
        
        if topic == "/sensor/temperature" and "value" in data:
            self.latest_data["temperature"] = data["value"]
            self.latest_data["timestamp"] = current_time
            logging.info(f"Updated temperature: {data['value']}")
        
        elif topic == "/sensor/pressure" and "value" in data:
            self.latest_data["pressure"] = data["value"]
            self.latest_data["timestamp"] = current_time
            logging.info(f"Updated pressure: {data['value']}")
        
        if self.latest_data["temperature"] is not None and self.latest_data["pressure"] is not None:
            self._check_thresholds()
    
    def _check_thresholds(self):
        temp = self.latest_data["temperature"]
        pressure = self.latest_data["pressure"]
        
        action = self.threshold_utils.get_valve_action(pressure, temp)
        
        if action:
            logging.info(f"Sending valve command: {action}")
            self.mqtt_handler.publish_valve_command(action)
            
            if self.threshold_utils.is_pressure_critical(pressure) or self.threshold_utils.is_temperature_critical(temp):
                self._notify_critical_situation(temp, pressure, action)
    
    def _notify_critical_situation(self, temperature, pressure, action):
        try:
            alert_data = {
                "source": "control_center",
                "type": "critical_values",
                "temperature": temperature,
                "pressure": pressure,
                "action_taken": action,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.catalog_url}/alerts",
                json=alert_data,
                timeout=5  # Add timeout
            )
            
            if response.status_code == 200 or response.status_code == 201:
                logging.info("Alert notification sent successfully")
            else:
                logging.warning(f"Failed to send alert notification: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            logging.warning("Resource Catalog not available - could not send alert")
        except Exception as e:
            logging.warning(f"Error sending alert notification: {str(e)}")
    
    def process_manual_command(self, command):
        if command not in ["OPEN", "CLOSE"]:
            logging.warning(f"Invalid valve command: {command}")
            return False
        
        logging.info(f"Processing manual valve command: {command}")
        return self.mqtt_handler.publish_valve_command(command)
    
    def get_latest_status(self):
        return {
            "latest_data": self.latest_data,
            "valve_recommendation": self.threshold_utils.get_valve_action(
                self.latest_data["pressure"] if self.latest_data["pressure"] is not None else 0,
                self.latest_data["temperature"] if self.latest_data["temperature"] is not None else 0
            )
        }