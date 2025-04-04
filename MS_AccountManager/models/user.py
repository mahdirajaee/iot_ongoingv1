import bcrypt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class User:
    """Simple user model for initial implementation"""
    # In-memory user storage (replace with database in production)
    _users = {}
    
    @classmethod
    def initialize_admin(cls):
        """Initialize admin user from environment variables"""
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "secure_password_here")
        
        # Check if admin already exists
        if admin_username not in cls._users:
            # Create admin user
            hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
            cls._users[admin_username] = {
                'username': admin_username,
                'password': hashed_password,
                'role': 'admin'
            }
            print(f"Admin user initialized: {admin_username}")
    
    @staticmethod
    def create(username, password, role='user'):
        """Create a new user"""
        if username in User._users:
            return False, "Username already exists"
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        User._users[username] = {
            'username': username,
            'password': hashed_password,
            'role': role
        }
        return True, User._users[username]
    
    @staticmethod
    def verify(username, password):
        """Verify user credentials"""
        if username not in User._users:
            return False, "Invalid username or password"
        
        user = User._users[username]
        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Return user data without password
            return True, {
                'username': user['username'],
                'role': user['role']
            }
        
        return False, "Invalid username or password"
    
    @staticmethod
    def get(username):
        """Get user by username"""
        user = User._users.get(username)
        if user:
            # Return user data without password
            return {
                'username': user['username'],
                'role': user['role']
            }
        return None

# Initialize admin user when module is imported
User.initialize_admin()