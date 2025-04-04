import os
import cherrypy
import json
import requests
from dotenv import load_dotenv
from controllers.auth_controller import AuthController

# Load environment variables
load_dotenv()

# Get configuration from environment variables
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8003))  # Each microservice needs a different port
RESOURCE_CATALOG_URL = os.getenv("RESOURCE_CATALOG_URL", "http://localhost:8001/catalog")

class AccountManagerService:
    def __init__(self):
        # Register with Resource Catalog
        self.register_with_catalog()
        
    def register_with_catalog(self):
        """Register this microservice with the Resource Catalog"""
        service_info = {
            "name": "AccountManager",
            "endpoint": f"http://{HOST}:{PORT}",
            "description": "Handles user authentication and authorization",
            "status": "active"
        }
        
        try:
            response = requests.post(
                f"{RESOURCE_CATALOG_URL}/services",
                json=service_info
            )
            if response.status_code == 200 or response.status_code == 201:
                print(f"Successfully registered with Resource Catalog")
            else:
                print(f"Failed to register with Resource Catalog: {response.text}")
        except Exception as e:
            print(f"Error registering with Resource Catalog: {str(e)}")

if __name__ == "__main__":
    # Configure CherryPy server
    cherrypy.config.update({
        'server.socket_host': HOST,
        'server.socket_port': PORT,
    })
    
    # Configure JSON handling
    cherrypy.tools.json_in = cherrypy._cptools.HandlerTool(cherrypy.lib.jsontools.json_in)
    cherrypy.tools.json_out = cherrypy._cptools.HandlerTool(cherrypy.lib.jsontools.json_out)
    
    # Mount the controllers
    cherrypy.tree.mount(
        AuthController(), '/auth',
        {'/': {'tools.json_in.on': True, 'tools.json_out.on': True}}
    )
    
    # Initialize service
    service = AccountManagerService()
    
    # Start the server
    cherrypy.engine.start()
    cherrypy.engine.block()