#!/usr/bin/env python3
"""
Resource Catalog Service for Smart IoT Bolt System
Python 3.11+ Entry Point
"""
import os
import sys
import logging
from typing import Dict, Any, Optional
import json 

# Apply patches for Python 3.13+ compatibility
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monkey_patch import apply_patches
apply_patches()

import cherrypy
from dotenv import load_dotenv

from controllers.catalog_controller import CatalogController

# Update version requirement to include Python 3.13
if sys.version_info < (3, 11):
    sys.exit("Error: This application requires Python 3.11 or newer")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('catalog_service.log')
    ]
)
logger = logging.getLogger('CatalogService')

# Load environment variables
load_dotenv()

# Get configuration from environment variables with defaults
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '8080'))
STORAGE_FILE = os.getenv('STORAGE_FILE', 'registry_data.json')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Set log level based on environment variable
numeric_level = getattr(logging, LOG_LEVEL.upper(), None)
if isinstance(numeric_level, int):
    logger.setLevel(numeric_level)

def main() -> None:
    """Main entry point for the application."""
    logger.info(f"Starting Resource Catalog service with Python {sys.version}")
    logger.info(f"Using storage file: {STORAGE_FILE}")
    
    # Server configuration
    conf: Dict[str, Any] = {
        'global': {
            'server.socket_host': HOST,
            'server.socket_port': PORT,
            'server.thread_pool': 10,
            'engine.autoreload.on': False,
            'log.screen': True,
            'log.access_file': 'access.log',
            'log.error_file': 'error.log'
        },
        '/': {
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')],
            'tools.encode.on': True,
            'tools.encode.encoding': 'utf-8',
            'tools.gzip.on': True,
        }
    }

    # Create and mount controller
    catalog_controller = CatalogController()
    cherrypy.tree.mount(catalog_controller, '/', conf)
    
    # Configure error handling
    cherrypy.config.update({'error_page.default': error_page})
    
    # Start the server
    cherrypy.engine.start()
    
    logger.info(f"Resource Catalog service started on http://{HOST}:{PORT}")
    
    try:
        cherrypy.engine.block()
    except KeyboardInterrupt:
        logger.info("Shutting down Resource Catalog service...")
        cherrypy.engine.stop()

def error_page(status: int, message: str, traceback: str, version: str) -> str:
    """Custom error page handler."""
    response = {
        "status": status,
        "message": message,
    }
    # Log the error
    if status >= 500:
        logger.error(f"Server error {status}: {message}\n{traceback}")
    
    return json.dumps(response)

if __name__ == '__main__':
    main()