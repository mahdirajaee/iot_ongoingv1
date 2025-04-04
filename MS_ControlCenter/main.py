import os
import cherrypy
import logging
import socket
from dotenv import load_dotenv
from controllers.control_controller import ControlController
from services.control_service import ControlService
from services.mqtt_handler import MQTTHandler
from utils.threshold_utils import ThresholdUtils

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()

def get_host_ip():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except:
        return "localhost"

def main():
    service_port = int(os.getenv("SERVICE_PORT", 8081))
    catalog_url = os.getenv("CATALOG_URL", "http://localhost:8080")
    
    mqtt_host = os.getenv("MQTT_BROKER_HOST", "localhost")
    mqtt_port = int(os.getenv("MQTT_BROKER_PORT", 1883))
    mqtt_client_id = os.getenv("MQTT_CLIENT_ID", "control_center")
    mqtt_username = os.getenv("MQTT_USERNAME", "")
    mqtt_password = os.getenv("MQTT_PASSWORD", "")
    
    pressure_min = float(os.getenv("PRESSURE_MIN_THRESHOLD", 30))
    pressure_max = float(os.getenv("PRESSURE_MAX_THRESHOLD", 150))
    temperature_min = float(os.getenv("TEMPERATURE_MIN_THRESHOLD", 10))
    temperature_max = float(os.getenv("TEMPERATURE_MAX_THRESHOLD", 80))
    
    threshold_utils = ThresholdUtils(
        pressure_min=pressure_min,
        pressure_max=pressure_max,
        temperature_min=temperature_min,
        temperature_max=temperature_max
    )
    
    control_service = ControlService(None, threshold_utils, catalog_url)
    
    host_ip = get_host_ip()
    control_service.update_service_info(host_ip, service_port)
    
    try:
        mqtt_handler = MQTTHandler(
            broker_host=mqtt_host,
            broker_port=mqtt_port,
            client_id=mqtt_client_id,
            on_message_callback=control_service.handle_sensor_data,
            username=mqtt_username if mqtt_username else None,
            password=mqtt_password if mqtt_password else None
        )
        
        control_service.mqtt_handler = mqtt_handler
        
        try:
            mqtt_handler.connect()
            logging.info("MQTT connection initialized")
        except Exception as e:
            logging.warning(f"Could not connect to MQTT broker: {str(e)} - Service will continue without MQTT")
    
    except Exception as e:
        logging.error(f"Error initializing MQTT: {str(e)}")
        logging.warning("Control Center will run without MQTT capabilities")
        mqtt_handler = None
    
    control_controller = ControlController(control_service)
    
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')],
        }
    }
    
    cherrypy.tree.mount(control_controller, '/api/control', conf)
    
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': service_port,
        'engine.autoreload.on': False
    })
    
    try:
        cherrypy.engine.start()
        logging.info(f"Control Center started on port {service_port}")
        cherrypy.engine.block()
    except KeyboardInterrupt:
        logging.info("Shutting down Control Center...")
    finally:
        if mqtt_handler:
            mqtt_handler.disconnect()
        cherrypy.engine.exit()

if __name__ == "__main__":
    main()