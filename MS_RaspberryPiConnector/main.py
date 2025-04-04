import os
import time
import logging
import threading
import signal
import sys
from dotenv import load_dotenv

from services.catalog_manager import CatalogManager
from services.actuator_service import ActuatorService
from services.mqtt_service import MQTTService
from services.sensor_service import SensorService
from services.rest_api import RaspberryPiAPI

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def main():
    load_dotenv()
    setup_logging()
    
    logging.info("Starting Raspberry Pi Connector")
    
    catalog_manager = CatalogManager()
    actuator_service = ActuatorService(catalog_manager)
    mqtt_service = MQTTService(actuator_service)
    sensor_service = SensorService(mqtt_service, catalog_manager)
    rest_api = RaspberryPiAPI(sensor_service, actuator_service)
    
    def graceful_shutdown(sig, frame):
        logging.info("Shutting down Raspberry Pi Connector...")
        sensor_service.stop()
        mqtt_service.disconnect()
        rest_api.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)
    
    # Connect to MQTT broker
    if not mqtt_service.connect():
        logging.error("Failed to connect to MQTT broker. Exiting.")
        sys.exit(1)
    
    # Register with the catalog
    registration_success = False
    max_retries = 5
    retry_count = 0
    
    while not registration_success and retry_count < max_retries:
        registration_success = catalog_manager.register_service()
        if not registration_success:
            retry_count += 1
            sleep_time = min(2 ** retry_count, 60)  # Exponential backoff with max 60 seconds
            logging.warning(f"Registration failed. Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
    
    if not registration_success:
        logging.error("Failed to register with catalog after multiple attempts. Continuing with default configuration.")
    
    # Get configuration from catalog
    config = catalog_manager.get_configuration()
    if config:
        sensor_service.update_config(config)
    
    # Start REST API
    rest_api.start()
    
    # Start sensor service
    sensor_service.start()
    
    # Periodically check for updated configurations
    def config_update_routine():
        while True:
            try:
                updated_config = catalog_manager.get_configuration()
                if updated_config:
                    sensor_service.update_config(updated_config)
                time.sleep(60)  # Check for updates every minute
            except Exception as e:
                logging.error(f"Error in configuration update routine: {e}")
                time.sleep(30)  # Retry after shorter delay on error
    
    config_thread = threading.Thread(target=config_update_routine)
    config_thread.daemon = True
    config_thread.start()
    
    logging.info("Raspberry Pi Connector is running")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        graceful_shutdown(None, None)

if __name__ == "__main__":
    main()