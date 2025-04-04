import cherrypy
import logging
import threading
import os
import sys
from functools import partial

from controllers.webhook_controller import WebhookController

class APIServer:
    def __init__(self, host, port, alert_service, loop):
        self.host = host
        self.port = port
        self.alert_service = alert_service
        self.loop = loop
        self.logger = logging.getLogger("TelegramBot.APIServer")
        self.server_thread = None
        
    def start(self):
        self.logger.info(f"Starting API server on {self.host}:{self.port}")
        
        # Configure CherryPy server with Python 3.13+ compatibility settings
        config = {
            'server.socket_host': self.host,
            'server.socket_port': self.port,
            'engine.autoreload.on': False,
            'log.screen': False,
        }
        
        # Add Python 3.13+ specific settings if needed
        if sys.version_info >= (3, 13):
            # Additional settings for Python 3.13+
            config.update({
                'tools.encode.on': True,
                'tools.encode.encoding': 'utf-8',
                'tools.response_headers.on': True,
            })
        
        cherrypy.config.update(config)
        
        # Create webhook controller
        webhook_controller = WebhookController(None, self.alert_service)
        
        # Mount the webhook controller
        cherrypy.tree.mount(
            webhook_controller, 
            '/', 
            {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}}
        )
        
        # Start CherryPy in a separate thread
        self.server_thread = threading.Thread(
            target=self._start_server,
            daemon=True
        )
        self.server_thread.start()
        
        self.logger.info("API server started")
    
    def _start_server(self):
        """Start CherryPy server with error handling"""
        try:
            cherrypy.engine.start()
        except Exception as e:
            self.logger.error(f"Error starting CherryPy server: {str(e)}")
            # Attempt to recover or notify about failure
            self._handle_server_failure(e)
    
    def _handle_server_failure(self, exception):
        """Handle server startup failure"""
        self.logger.error(f"Server failed to start: {str(exception)}")
        # Could implement recovery logic here if needed
    
    def stop(self):
        """Stop the CherryPy server"""
        self.logger.info("Stopping API server")
        try:
            cherrypy.engine.exit()
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5.0)
        except Exception as e:
            self.logger.error(f"Error stopping CherryPy server: {str(e)}") 