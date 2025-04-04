import cherrypy
import json

class ControlController:
    def __init__(self, control_service):
        self.control_service = control_service
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def command(self):
        if cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            
            if "command" not in data:
                raise cherrypy.HTTPError(400, "Missing 'command' field")
            
            command = data["command"].upper()
            
            if command not in ["OPEN", "CLOSE"]:
                raise cherrypy.HTTPError(400, "Invalid command. Must be 'OPEN' or 'CLOSE'")
            
            success = self.control_service.process_manual_command(command)
            
            if success:
                return {"status": "success", "message": f"Command {command} sent successfully"}
            else:
                raise cherrypy.HTTPError(500, "Failed to send command")
        else:
            raise cherrypy.HTTPError(405, "Method not allowed")
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def status(self):
        if cherrypy.request.method == 'GET':
            return self.control_service.get_latest_status()
        else:
            raise cherrypy.HTTPError(405, "Method not allowed")