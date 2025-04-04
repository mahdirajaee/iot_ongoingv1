import cherrypy
import json
import os
import logging

class RaspberryPiAPI:
    def __init__(self, sensor_service, actuator_service):
        self.sensor_service = sensor_service
        self.actuator_service = actuator_service
        self.port = int(os.getenv("SERVICE_PORT", 8081))

    def start(self):
        config = {
            'global': {
                'server.socket_host': '0.0.0.0',
                'server.socket_port': self.port,
                'engine.autoreload.on': False,
            },
            '/': {
                'tools.response_headers.on': True,
                'tools.response_headers.headers': [('Content-Type', 'application/json')],
            }
        }
        
        cherrypy.tree.mount(SensorResource(self.sensor_service), '/api/sensors', config)
        cherrypy.tree.mount(ActuatorResource(self.actuator_service), '/api/actuator', config)
        
        cherrypy.engine.start()
        logging.info(f"REST API started on port {self.port}")
    
    def stop(self):
        cherrypy.engine.exit()
        logging.info("REST API stopped")


class SensorResource:
    def __init__(self, sensor_service):
        self.sensor_service = sensor_service
    
    @cherrypy.expose
    def index(self):
        readings = self.sensor_service.get_sensor_readings()
        return json.dumps(readings)


class ActuatorResource:
    def __init__(self, actuator_service):
        self.actuator_service = actuator_service
    
    @cherrypy.expose
    def valve(self, **kwargs):
        if cherrypy.request.method == 'GET':
            state = self.actuator_service.get_valve_state()
            return json.dumps(state)
        elif cherrypy.request.method == 'POST':
            try:
                data = json.loads(cherrypy.request.body.read().decode('utf-8'))
                if 'state' not in data:
                    raise cherrypy.HTTPError(400, "Missing 'state' parameter")
                
                result = self.actuator_service.set_valve_state(data['state'])
                if result:
                    return json.dumps({"success": True})
                else:
                    raise cherrypy.HTTPError(400, "Invalid valve state. Must be 'open' or 'closed'")
            except json.JSONDecodeError:
                raise cherrypy.HTTPError(400, "Invalid JSON in request body")
    
    valve.exposed = True