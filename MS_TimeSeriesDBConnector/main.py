import os
import json
import logging
import threading
import time
import requests

# Import compatibility module for Python 3.13.1 first
import sys
if sys.version_info >= (3, 13):
    from utils.cherrypy_compat import *
    
import cherrypy
from dotenv import load_dotenv
from services.influxdb_service import InfluxDBService
from services.mqtt_listener import MQTTListener
from controllers.data_controller import DataController

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CatalogRegistrationThread(threading.Thread):
    def __init__(self, host, port):
        """
        Initialize service registration thread
        
        Args:
            host (str): Service host
            port (int): Service port
        """
        super().__init__()  # Updated to use super() for Python 3.13.1 compatibility
        self.host = host
        self.port = port
        self.daemon = True
        self.catalog_url = os.getenv('CATALOG_URL')
        self.service_name = os.getenv('SERVICE_NAME')
        self.service_type = os.getenv('SERVICE_TYPE')
        
    def run(self):
        """Run thread to periodically register service with Resource Catalog"""
        while True:
            try:
                # Service information
                service_info = {
                    "name": self.service_name,
                    "type": self.service_type,
                    "endpoint": f"http://{self.host}:{self.port}",
                    "apis": {
                        "temperature": f"http://{self.host}:{self.port}/api/v1/data/temperature",
                        "pressure": f"http://{self.host}:{self.port}/api/v1/data/pressure",
                        "latest": f"http://{self.host}:{self.port}/api/v1/data/latest"
                    }
                }
                
                # Register with catalog
                response = requests.post(
                    f"{self.catalog_url}/api/v1/services/register",
                    json=service_info,
                    timeout=10  # Added timeout for requests
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully registered with Resource Catalog at {self.catalog_url}")
                else:
                    logger.error(f"Failed to register with Resource Catalog: {response.text}")
                    
            except Exception as e:
                logger.error(f"Error registering with Resource Catalog: {e}")
                
            # Sleep for 60 seconds before re-registering
            time.sleep(60)

def main():
    """Main entry point"""
    try:
        # Get environment variables
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8081))
        
        # Initialize services
        influxdb_service = InfluxDBService()
        mqtt_listener = MQTTListener(influxdb_service)
        
        # Connect to MQTT broker
        mqtt_listener.connect()
        
        # Initialize API controllers
        data_controller = DataController(influxdb_service)
        
        # Configure CherryPy
        conf = {
            '/': {
                'tools.sessions.on': True,
                'tools.staticdir.root': os.path.abspath(os.getcwd())
            },
            '/api/v1/data': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.response_headers.on': True,
                'tools.response_headers.headers': [('Content-Type', 'application/json')],
            }
        }
        
        # Mount controllers
        cherrypy.tree.mount(data_controller, '/api/v1/data', conf)
        
        # Start service registration thread
        registration_thread = CatalogRegistrationThread(host, port)
        registration_thread.start()
        
        # Configure server
        cherrypy.config.update({
            'server.socket_host': host,
            'server.socket_port': port,
            'engine.autoreload.on': False,
            'log.screen': True,
            'tools.sessions.secure': True,  # Add secure sessions for Python 3.13.1
            'tools.sessions.httponly': True  # Add httponly flag for Python 3.13.1
        })
        
        # Start CherryPy server
        logger.info(f"Starting Time Series DB Connector on {host}:{port}")
        cherrypy.engine.signals.subscribe()  # Ensure signal handlers are registered
        cherrypy.engine.start()
        cherrypy.engine.block()
        
    except Exception as e:
        logger.error(f"Error starting service: {e}")
    finally:
        # Cleanup
        if 'mqtt_listener' in locals():
            mqtt_listener.disconnect()
        if cherrypy.engine.state != cherrypy.engine.states.STOPPED:
            cherrypy.engine.stop()

if __name__ == "__main__":
    main()