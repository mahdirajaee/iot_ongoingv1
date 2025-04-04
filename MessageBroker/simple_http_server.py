#!/usr/bin/env python3
"""
Simple HTTP API Server for Smart IoT Bolt Dashboard

This server provides HTTP REST endpoints for the dashboard to access real-time data
without using WebSockets or any third-party libraries that might have compatibility
issues with Python 3.13.

Usage:
    python simple_http_server.py [--no-mqtt] [--port PORT] [--interval INTERVAL]

Options:
    --no-mqtt        Run without MQTT broker (use test data generator)
    --port PORT      HTTP server port (default: 8088)
    --interval       Test data generation interval in seconds (default: 3.0)
"""

import http.server
import socketserver
import json
import paho.mqtt.client as mqtt
import threading
import time
import os
import argparse
import urllib.parse
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

# Custom HTTP request handler
class APIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, data_store=None, mqtt_handler=None, **kwargs):
        self.data_store = data_store
        self.mqtt_handler = mqtt_handler
        super().__init__(*args, **kwargs)
    
    def send_cors_headers(self):
        """Add CORS headers to allow any origin"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def send_json_response(self, data, status=200):
        """Send a JSON response with proper headers"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests to API endpoints"""
        path = urllib.parse.urlparse(self.path).path
        
        # Root path - show available endpoints
        if path == '/' or path == '/api':
            self.send_json_response({
                "message": "Smart IoT Bolt Dashboard API Server",
                "endpoints": [
                    "/api/data",
                    "/api/temperature",
                    "/api/pressure", 
                    "/api/valves",
                    "/api/valve/{valve_id}"
                ]
            })
            return
        
        # All data endpoint
        elif path == '/api/data':
            self.send_json_response({
                "temperature": self.data_store.temperature,
                "pressure": self.data_store.pressure,
                "valves": self.data_store.valves,
                "timestamp": self.data_store.last_update
            })
            return
        
        # Temperature endpoint
        elif path == '/api/temperature':
            self.send_json_response(self.data_store.temperature)
            return
        
        # Pressure endpoint
        elif path == '/api/pressure':
            self.send_json_response(self.data_store.pressure)
            return
        
        # Valves endpoint
        elif path == '/api/valves':
            self.send_json_response(self.data_store.valves)
            return
        
        # Valve specific endpoint
        elif path.startswith('/api/valve/'):
            valve_id = path.replace('/api/valve/', '')
            if valve_id in self.data_store.valves:
                self.send_json_response(self.data_store.valves[valve_id])
            else:
                self.send_json_response({"error": "Valve not found"}, 404)
            return
        
        # Not found
        else:
            self.send_json_response({"error": "Endpoint not found"}, 404)
            return
    
    def do_POST(self):
        """Handle POST requests to API endpoints"""
        path = urllib.parse.urlparse(self.path).path
        
        # Valve specific endpoint for control
        if path.startswith('/api/valve/'):
            valve_id = path.replace('/api/valve/', '')
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                # Parse JSON body
                data = json.loads(body)
                
                # Check for required status field
                if 'status' not in data:
                    self.send_json_response({"error": "Status is required"}, 400)
                    return
                
                # Update valve status
                status = data['status']
                if self.mqtt_handler.publish_valve_status(valve_id, status):
                    self.send_json_response({
                        "id": valve_id,
                        "status": status,
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "message": f"Valve {valve_id} status updated to {status}"
                    })
                else:
                    self.send_json_response({"error": "Failed to update valve status"}, 500)
                
            except json.JSONDecodeError:
                self.send_json_response({"error": "Invalid JSON payload"}, 400)
            except Exception as e:
                self.send_json_response({"error": str(e)}, 500)
            
            return
        
        # Not found or method not allowed
        else:
            self.send_json_response({"error": "Endpoint not found or method not allowed"}, 404)
            return

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
    
    # Create HTTP server with handler factory
    handler_factory = lambda *args, **kwargs: APIHandler(*args, data_store=data_store, mqtt_handler=mqtt_handler, **kwargs)
    
    # Create server with our custom handler
    with socketserver.ThreadingTCPServer(("", args.port), handler_factory) as httpd:
        print(f"Starting HTTP API server on port {args.port}")
        print("API endpoints:")
        print(f"  - http://localhost:{args.port}/api/data")
        print(f"  - http://localhost:{args.port}/api/temperature")
        print(f"  - http://localhost:{args.port}/api/pressure")
        print(f"  - http://localhost:{args.port}/api/valves")
        print(f"  - http://localhost:{args.port}/api/valve/{{valve_id}} (GET/POST)")
        print("\nUse Ctrl+C to stop the server")
        
        try:
            # Start the server
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Stopping server...")
            httpd.server_close()

if __name__ == "__main__":
    main() 