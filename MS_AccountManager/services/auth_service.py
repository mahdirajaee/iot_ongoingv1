import os
from models.user import User
from utils.token_utils import generate_token, verify_token as verify_jwt

class AuthService:
    def authenticate_user(self, username, password):
        """Authenticate a user and return a JWT token"""
        success, result = User.verify(username, password)
        
        if not success:
            raise Exception(result)
        
        # Generate a JWT token
        token = generate_token(result)
        
        return {
            'token': token,
            'user': result
        }
    
    def verify_token(self, token):
        """Verify a JWT token and return user information"""
        try:
            # Decode and verify the token
            payload = verify_jwt(token)
            
            if not payload:
                return None
            
            # Get user information
            username = payload.get('username')
            if not username:
                return None
            
            user = User.get(username)
            return user
        except Exception as e:
            return None
    
    def register_user(self, username, password, role='user'):
        """Register a new user"""
        success, result = User.create(username, password, role)
        
        if not success:
            raise Exception(result)
        
        return {
            'message': 'User registered successfully',
            'user': {
                'username': result['username'],
                'role': result['role']
            }
        }