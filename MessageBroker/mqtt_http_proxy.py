#!/usr/bin/env python3
"""
Smart IoT Bolt Dashboard HTTP API Server

This server provides HTTP REST endpoints for the dashboard to access real-time data
without using WebSockets. It can connect to an MQTT broker or generate test data
if no broker is available.

Usage:
    python mqtt_http_proxy.py [--no-mqtt] [--port PORT] [--interval INTERVAL]

Options:
    --no-mqtt        Run without MQTT broker (use test data generator)
    --port PORT      HTTP server port (default: 8088)
    --interval       Test data generation interval in seconds (default: 3.0)
"""

# CherryPy 18.9.0 now handles Python 3.13+ compatibility
import sys
import cherrypy
import paho.mqtt.client as mqtt
import json
import threading
import time
import os
import argparse
import io
from dotenv import load_dotenv

# Import the test data generator
try:
    from test_data_generator import TestDataGenerator
except ImportError:
    # If running from a different directory, adjust the import
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from test_data_generator import TestDataGenerator

load_dotenv()

# Store the latest data from MQTT topics
class DataStore:
    def __init__(self):
        self.temperature = {}
        self.pressure = {}
        self.valves = {}
        self.last_update = time.time()

# MQTT Client handler
class MQTTHandler:
    def __init__(self, data_store):
        self.data_store = data_store
        self.mqtt_host = os.getenv('MQTT_HOST', 'localhost')
        self.mqtt_port = int(os.getenv('MQTT_PORT', 1883))
        self.client = None
        self.connected = False
    
    def start(self):
        """Start the MQTT connection"""
        # Setup MQTT client
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)  # Explicitly use VERSION1 API
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        # Start connection in a separate thread
        self.mqtt_thread = threading.Thread(target=self.start_mqtt)
        self.mqtt_thread.daemon = True
        self.mqtt_thread.start()
    
    def start_mqtt(self):
        try:
            print(f"Connecting to MQTT broker at {self.mqtt_host}:{self.mqtt_port}")
            self.client.connect(self.mqtt_host, self.mqtt_port, 60)
            self.client.loop_forever()
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            self.connected = False
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
            self.connected = True
            # Subscribe to topics
            client.subscribe("/sensor/temperature")
            client.subscribe("/sensor/pressure")
            client.subscribe("/actuator/valve")
            print("Subscribed to sensor and actuator topics")
        else:
            print(f"Failed to connect to MQTT broker with code: {rc}")
            self.connected = False
    
    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            if topic == "/sensor/temperature":
                self.data_store.temperature = payload
            elif topic == "/sensor/pressure":
                self.data_store.pressure = payload
            elif topic == "/actuator/valve":
                valve_id = payload.get("id", "unknown")
                self.data_store.valves[valve_id] = payload
            
            self.data_store.last_update = time.time()
            
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def publish_valve_status(self, valve_id, status):
        """Publish valve status change to MQTT broker"""
        try:
            payload = {
                "id": valve_id,
                "status": status,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
            
            # Update local data store
            self.data_store.valves[valve_id] = payload
            
            # Publish to MQTT if connected
            if self.client and self.connected:
                self.client.publish("/actuator/valve", json.dumps(payload))
                print(f"Published valve status to MQTT: {valve_id} is {status}")
            else:
                print(f"Updated valve status locally (no MQTT): {valve_id} is {status}")
            
            return True
        except Exception as e:
            print(f"Error publishing valve status: {e}")
            return False

# CherryPy API Server
class APIServer:
    def __init__(self, data_store, mqtt_handler):
        self.data_store = data_store
        self.mqtt_handler = mqtt_handler
    
    @cherrypy.expose
    def index(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps({
            "message": "Smart IoT Bolt Dashboard API Server",
            "endpoints": [
                "/api/data",
                "/api/temperature",
                "/api/pressure",
                "/api/valves",
                "/api/valve/{valve_id}"
            ]
        })
    
    @cherrypy.expose
    def api(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return self.index()
    
    @cherrypy.expose
    def data(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        # Add CORS headers
        self._add_cors_headers()
        return json.dumps({
            "temperature": self.data_store.temperature,
            "pressure": self.data_store.pressure,
            "valves": self.data_store.valves,
            "timestamp": self.data_store.last_update
        })
    
    @cherrypy.expose
    def temperature(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        self._add_cors_headers()
        return json.dumps(self.data_store.temperature)
    
    @cherrypy.expose
    def pressure(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        self._add_cors_headers()
        return json.dumps(self.data_store.pressure)
    
    @cherrypy.expose
    def valves(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        self._add_cors_headers()
        return json.dumps(self.data_store.valves)
    
    @cherrypy.expose
    def valve(self, valve_id=None):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        self._add_cors_headers()
        
        # OPTIONS request handling for CORS preflight
        if cherrypy.request.method == 'OPTIONS':
            return ''
        
        # GET request - return valve status
        if cherrypy.request.method == 'GET':
            if valve_id and valve_id in self.data_store.valves:
                return json.dumps(self.data_store.valves[valve_id])
            else:
                cherrypy.response.status = 404
                return json.dumps({"error": "Valve not found"})
        
        # POST request - update valve status
        elif cherrypy.request.method == 'POST':
            try:
                # Get request body as bytes and decode
                cl = cherrypy.request.headers.get('Content-Length', 0)
                raw_body = cherrypy.request.body.read(int(cl))
                body_str = raw_body.decode('utf-8')
                
                # Parse JSON
                body = json.loads(body_str)
                
                # Validate request
                if not valve_id:
                    cherrypy.response.status = 400
                    return json.dumps({"error": "Valve ID is required"})
                
                if "status" not in body:
                    cherrypy.response.status = 400
                    return json.dumps({"error": "Status is required"})
                
                # Update valve status
                if self.mqtt_handler.publish_valve_status(valve_id, body["status"]):
                    return json.dumps({
                        "id": valve_id,
                        "status": body["status"],
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "message": f"Valve {valve_id} status updated to {body['status']}"
                    })
                else:
                    cherrypy.response.status = 500
                    return json.dumps({"error": "Failed to update valve status"})
                
            except json.JSONDecodeError:
                cherrypy.response.status = 400
                return json.dumps({"error": "Invalid JSON payload"})
            except Exception as e:
                cherrypy.response.status = 500
                return json.dumps({"error": str(e)})
        
        # Method not allowed
        else:
            cherrypy.response.status = 405
            return json.dumps({"error": "Method not allowed"})
    
    def _add_cors_headers(self):
        """Add CORS headers to the response"""
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        cherrypy.response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        cherrypy.response.headers["Access-Control-Allow-Headers"] = "Content-Type"

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='HTTP API server for Smart IoT Bolt Dashboard')
    parser.add_argument('--no-mqtt', action='store_true', help='Run without MQTT broker (use test data generator)')
    parser.add_argument('--port', type=int, default=8088, help='HTTP server port (default: 8088)')
    parser.add_argument('--interval', type=float, default=3.0, help='Test data generation interval in seconds (default: 3.0)')
    return parser.parse_args()

def main():
    # Parse arguments
    args = parse_arguments()
    
    # Create data store
    data_store = DataStore()
    
    # Create MQTT handler
    mqtt_handler = MQTTHandler(data_store)
    
    # Start data sources
    if args.no_mqtt:
        print("Running without MQTT broker - using test data generator")
        try:
            # Create and start the test data generator
            data_generator = TestDataGenerator(data_store)
            data_generator.start(interval=args.interval)
        except Exception as e:
            print(f"Error starting test data generator: {e}")
            print("Will proceed with empty data")
    else:
        print("Starting MQTT handler")
        mqtt_handler.start()
    
    # Configure CherryPy to work with Python 3.13
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': args.port,
        'tools.sessions.on': False,
        'engine.autoreload.on': False  # Disable autoreload which can cause issues
    })
    
    # Configure API CORS as a tool that can be applied to specific paths
    cors_config = {
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type')
        ],
    }
    
    # Mount the API server
    api = APIServer(data_store, mqtt_handler)
    
    # Use a dispatcher to route api/ URLs to the same methods
    d = cherrypy.dispatch.RoutesDispatcher()
    d.connect('index', '/', controller=api, action='index')
    d.connect('api_index', '/api/', controller=api, action='index')
    d.connect('data', '/api/data', controller=api, action='data')
    d.connect('temperature', '/api/temperature', controller=api, action='temperature')
    d.connect('pressure', '/api/pressure', controller=api, action='pressure')
    d.connect('valves', '/api/valves', controller=api, action='valves')
    d.connect('valve', '/api/valve/{valve_id}', controller=api, action='valve')
    
    # Mount with dispatcher
    config = {
        '/': {
            'request.dispatch': d,
            **cors_config,
        }
    }
    
    cherrypy.tree.mount(root=None, config=config)
    
    # Start the server
    try:
        print(f"Starting HTTP API server on port {args.port}")
        print("API endpoints:")
        print(f"  - http://localhost:{args.port}/api/data")
        print(f"  - http://localhost:{args.port}/api/temperature")
        print(f"  - http://localhost:{args.port}/api/pressure")
        print(f"  - http://localhost:{args.port}/api/valves")
        print(f"  - http://localhost:{args.port}/api/valve/{{valve_id}} (GET/POST)")
        print("\nUse Ctrl+C to stop the server")
        
        cherrypy.engine.start()
        cherrypy.engine.block()
    except KeyboardInterrupt:
        print("Stopping server...")
        cherrypy.engine.stop()

if __name__ == "__main__":
    main()