import time
import os
import logging
import datetime
import threading
from utils.gaussian import generate_gaussian_value

class SensorService:
    def __init__(self, mqtt_service, catalog_manager):
        self.mqtt_service = mqtt_service
        self.catalog_manager = catalog_manager
        self.temperature_mean = float(os.getenv("TEMPERATURE_MEAN", 70))
        self.temperature_std = float(os.getenv("TEMPERATURE_STD", 5))
        self.pressure_mean = float(os.getenv("PRESSURE_MEAN", 100))
        self.pressure_std = float(os.getenv("PRESSURE_STD", 10))
        self.publish_interval = int(os.getenv("SENSOR_PUBLISH_INTERVAL", 5))
        self.running = False
        self.publish_thread = None
        self.last_temperature = None
        self.last_pressure = None

    def start(self):
        self.running = True
        self.publish_thread = threading.Thread(target=self._publish_sensor_data)
        self.publish_thread.daemon = True
        self.publish_thread.start()
        logging.info(f"Sensor service started with publish interval: {self.publish_interval} seconds")

    def stop(self):
        self.running = False
        if self.publish_thread:
            self.publish_thread.join(timeout=5)
        logging.info("Sensor service stopped")

    def update_config(self, config):
        if "temperature_mean" in config:
            self.temperature_mean = float(config["temperature_mean"])
        if "temperature_std" in config:
            self.temperature_std = float(config["temperature_std"])
        if "pressure_mean" in config:
            self.pressure_mean = float(config["pressure_mean"])
        if "pressure_std" in config:
            self.pressure_std = float(config["pressure_std"])
        if "publish_interval" in config:
            self.publish_interval = int(config["publish_interval"])
        
        logging.info(f"Sensor configuration updated: T({self.temperature_mean}±{self.temperature_std}), "
                     f"P({self.pressure_mean}±{self.pressure_std}), Interval: {self.publish_interval}s")

    def _generate_sensor_readings(self):
        self.last_temperature = generate_gaussian_value(
            self.temperature_mean, self.temperature_std, min_val=0)
        self.last_pressure = generate_gaussian_value(
            self.pressure_mean, self.pressure_std, min_val=0)
        
        return self.last_temperature, self.last_pressure

    def _publish_sensor_data(self):
        while self.running:
            try:
                temperature, pressure = self._generate_sensor_readings()
                timestamp = datetime.datetime.now().isoformat()
                
                self.mqtt_service.publish_temperature(temperature, timestamp)
                self.mqtt_service.publish_pressure(pressure, timestamp)
                
                self.catalog_manager.update_sensor_status({
                    "temperature": temperature,
                    "pressure": pressure,
                    "timestamp": timestamp
                })
                
                time.sleep(self.publish_interval)
            except Exception as e:
                logging.error(f"Error in sensor data publishing: {e}")
                time.sleep(5)  # Retry after a short delay

    def get_sensor_readings(self):
        return {
            "temperature": self.last_temperature,
            "pressure": self.last_pressure,
            "timestamp": datetime.datetime.now().isoformat()
        }