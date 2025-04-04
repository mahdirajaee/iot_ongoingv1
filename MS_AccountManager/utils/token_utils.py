import os
import jwt
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get JWT configuration from environment variables
JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret_key_here")
JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", 3600))  # Default: 1 hour

def generate_token(user_data):
    """Generate a JWT token for the user"""
    payload = {
        'username': user_data['username'],
        'role': user_data['role'],
        'exp': int(time.time()) + JWT_EXPIRATION,  # Expiration time
        'iat': int(time.time())  # Issued at time
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token

def verify_token(token):
    """Verify a JWT token and return the payload if valid"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Invalid token
        return None