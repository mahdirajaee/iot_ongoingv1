import cherrypy
import os
import sys
from dotenv import load_dotenv
from controllers.analytics_controller import get_app

load_dotenv()

def main():
    port = int(os.getenv("SERVICE_PORT", 8083))
    
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': port,
        'engine.autoreload.on': True,
        'log.screen': True,
    })
    
    app = get_app()
    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == '__main__':
    main()