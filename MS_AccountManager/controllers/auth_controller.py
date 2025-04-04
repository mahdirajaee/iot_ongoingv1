import cherrypy
import json
from services.auth_service import AuthService

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def login(self):
        """Endpoint for user login"""
        try:
            data = cherrypy.request.json
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                raise cherrypy.HTTPError(400, "Username and password are required")
                
            result = self.auth_service.authenticate_user(username, password)
            return result
        except Exception as e:
            if isinstance(e, cherrypy.HTTPError):
                raise
            cherrypy.log(f"Error in login: {str(e)}")
            raise cherrypy.HTTPError(500, f"Internal server error: {str(e)}")
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def verify(self, token=None):
        """Endpoint to verify a token"""
        try:
            if not token:
                raise cherrypy.HTTPError(400, "Token is required")
                
            result = self.auth_service.verify_token(token)
            if not result:
                raise cherrypy.HTTPError(401, "Invalid or expired token")
            return result
        except Exception as e:
            if isinstance(e, cherrypy.HTTPError):
                raise
            cherrypy.log(f"Error in verify: {str(e)}")
            raise cherrypy.HTTPError(500, f"Internal server error: {str(e)}")
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def register(self):
        """Endpoint for user registration (admin only)"""
        try:
            data = cherrypy.request.json
            admin_token = cherrypy.request.headers.get('Authorization')
            
            if not admin_token:
                raise cherrypy.HTTPError(401, "Authentication required")
                
            # Strip 'Bearer ' prefix if present
            if admin_token.startswith('Bearer '):
                admin_token = admin_token[7:]
            
            # Verify admin privileges
            admin_check = self.auth_service.verify_token(admin_token)
            if not admin_check or admin_check.get('role') != 'admin':
                raise cherrypy.HTTPError(403, "Admin privileges required")
            
            # Process registration
            username = data.get('username')
            password = data.get('password')
            role = data.get('role', 'user')  # Default to 'user' role
            
            if not username or not password:
                raise cherrypy.HTTPError(400, "Username and password are required")
                
            result = self.auth_service.register_user(username, password, role)
            return result
        except Exception as e:
            if isinstance(e, cherrypy.HTTPError):
                raise
            cherrypy.log(f"Error in register: {str(e)}")
            raise cherrypy.HTTPError(500, f"Internal server error: {str(e)}")