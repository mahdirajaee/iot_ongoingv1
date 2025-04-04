/**
 * auth.js - Authentication functionality for Smart IoT Bolt Dashboard
 */

const Auth = (function() {
  'use strict';
  
  // Storage keys
  const STORAGE_KEYS = {
    TOKEN: 'auth_token',
    TOKEN_CREATED: 'auth_token_created',
    USER: 'user',
    REMEMBER: 'remember_login'
  };
  
  // Token expiration time (24 hours)
  const TOKEN_EXPIRATION = 24 * 60 * 60 * 1000;
  
  // Check if user is authenticated
  function isAuthenticated() {
    console.log("Checking authentication...");
    const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
    const tokenCreated = localStorage.getItem(STORAGE_KEYS.TOKEN_CREATED);
    
    console.log("Token found:", !!token);
    console.log("Token created timestamp:", tokenCreated);
    
    if (!token || !tokenCreated) {
      console.log("No token or creation timestamp found");
      return false;
    }
    
    // Check token expiration
    const tokenAge = Date.now() - parseInt(tokenCreated);
    console.log("Token age (ms):", tokenAge);
    console.log("Token expiration (ms):", TOKEN_EXPIRATION);
    
    if (tokenAge > TOKEN_EXPIRATION) {
      // Token expired, clear auth data
      console.log("Token expired, clearing auth data");
      clearAuthData(false);
      return false;
    }
    
    console.log("Token is valid");
    return true;
  }
  
  // Handle login form submission
  function login(username, password, rememberMe = false) {
    console.log("Login attempt for username:", username);
    console.log("Remember me:", rememberMe);
    
    return new Promise((resolve, reject) => {
      // Validation
      if (!username || username.length < 3) {
        reject({ message: 'Username must be at least 3 characters' });
        return;
      }
      
      if (!password || password.length < 6) {
        reject({ message: 'Password must be at least 6 characters' });
        return;
      }
      
      // Simulate API call
      setTimeout(() => {
        console.log("Login simulation completed");
        // Demo - accept any username/password combo that meets requirements
        const userData = {
          name: formatName(username),
          username: username,
          avatar: getInitials(username),
          role: 'User'
        };
        
        // Store authentication data
        const mockToken = generateToken();
        const timestamp = Date.now().toString();
        
        console.log("Storing auth data:");
        console.log("Token:", mockToken);
        console.log("Token created:", timestamp);
        console.log("User data:", userData);
        
        localStorage.setItem(STORAGE_KEYS.TOKEN, mockToken);
        localStorage.setItem(STORAGE_KEYS.TOKEN_CREATED, timestamp);
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(userData));
        
        // Verify storage
        console.log("Verifying localStorage:");
        console.log("Token stored:", localStorage.getItem(STORAGE_KEYS.TOKEN));
        console.log("Token created stored:", localStorage.getItem(STORAGE_KEYS.TOKEN_CREATED));
        console.log("User data stored:", localStorage.getItem(STORAGE_KEYS.USER));
        
        // Store remember preference
        if (rememberMe) {
          localStorage.setItem(STORAGE_KEYS.REMEMBER, 'true');
        } else {
          localStorage.removeItem(STORAGE_KEYS.REMEMBER);
        }
        
        resolve({
          success: true,
          message: 'Login successful',
          user: userData
        });
      }, 1000);
    });
  }
  
  // Handle logout
  function logout() {
    clearAuthData(true);
    window.location.href = 'login.html';
  }
  
  // Clear authentication data
  function clearAuthData(clearAll = false) {
    localStorage.removeItem(STORAGE_KEYS.TOKEN);
    localStorage.removeItem(STORAGE_KEYS.TOKEN_CREATED);
    localStorage.removeItem(STORAGE_KEYS.USER);
    
    // Only clear remember preference if explicitly requested
    if (clearAll) {
      localStorage.removeItem(STORAGE_KEYS.REMEMBER);
    }
  }
  
  // Get stored user data
  function getUserData() {
    const userData = localStorage.getItem(STORAGE_KEYS.USER);
    return userData ? JSON.parse(userData) : null;
  }
  
  // Check if token is about to expire
  function isTokenExpiringSoon(thresholdMinutes = 30) {
    const tokenCreated = localStorage.getItem(STORAGE_KEYS.TOKEN_CREATED);
    if (!tokenCreated) return false;
    
    const expirationTime = parseInt(tokenCreated) + TOKEN_EXPIRATION;
    const timeRemaining = expirationTime - Date.now();
    const thresholdMs = thresholdMinutes * 60 * 1000;
    
    return timeRemaining > 0 && timeRemaining < thresholdMs;
  }
  
  // Helper: Format name from username
  function formatName(username) {
    const parts = username.split(/[._-]/);
    if (parts.length > 1) {
      return `${capitalize(parts[0])} ${capitalize(parts[1])}`;
    }
    return capitalize(username);
  }
  
  // Helper: Capitalize first letter
  function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
  
  // Helper: Get initials from name
  function getInitials(name) {
    const parts = name.split(/[._\s-]/);
    if (parts.length > 1) {
      return (parts[0].charAt(0) + parts[1].charAt(0)).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  }
  
  // Helper: Generate mock token
  function generateToken() {
    return 'mock_token_' + Math.random().toString(36).substr(2, 16);
  }
  
  // Public API
  return {
    isAuthenticated,
    login,
    logout,
    getUserData,
    isTokenExpiringSoon
  };
})();

// Add login form handler when on login page
document.addEventListener('DOMContentLoaded', () => {
  console.log("DOM content loaded, looking for login form");
  const loginForm = document.getElementById('loginForm');
  
  if (loginForm) {
    console.log("Login form found, attaching event listener");
    loginForm.addEventListener('submit', handleLoginSubmit);
    
    // Initialize password toggle
    const togglePassword = document.getElementById('togglePassword');
    if (togglePassword) {
      togglePassword.addEventListener('click', () => {
        const passwordInput = document.getElementById('password');
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);        
        // Toggle icon
        const icon = togglePassword.querySelector('i');
        if (icon) {
          icon.classList.toggle('fa-eye');
          icon.classList.toggle('fa-eye-slash');
        }
      });
    }
    
    // Check for expired session notification
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('expired') === 'true') {
      showLoginMessage('Your session has expired. Please log in again.', 'warning');
    }
  } else {
    console.log("Login form not found on this page");
  }
  
  // Check if we're on the dashboard and need to redirect
  if (window.location.href.includes('dashboard.html')) {
    console.log("On dashboard page, checking authentication");
    if (!Auth.isAuthenticated()) {
      console.log("Not authenticated, redirecting to login");
      window.location.href = 'login.html';
    } else {
      console.log("Authentication verified for dashboard");
    }
  }
});

// Handle login form submission
function handleLoginSubmit(e) {
  e.preventDefault();
  
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  const rememberMe = document.getElementById('rememberMe')?.checked || false;
  
  // Reset field highlighting
  resetFieldHighlights();
  
  // Show loading state
  showLoginMessage('Authenticating...', 'loading');
  
  // Attempt login
  Auth.login(username, password, rememberMe)
    .then(response => {
      showLoginMessage('Login successful! Redirecting...', 'success');
      
      // Redirect to dashboard
      setTimeout(() => {
        window.location.href = 'dashboard.html';
      }, 1000);
    })
    .catch(error => {
      console.error('Login error:', error);
      showLoginMessage(error.message || 'Authentication failed. Please try again.', 'error');
      
      // Highlight field if specified
      if (error.field) {
        highlightField(error.field);
      }
    });
}

// Show login message
function showLoginMessage(message, type) {
  const loginMessage = document.getElementById('loginMessage');
  if (!loginMessage) return;
  
  loginMessage.textContent = message;
  loginMessage.style.display = 'block';
  loginMessage.className = 'login-message';
  
  if (type) {
    loginMessage.classList.add(type);
    
    // Add loading spinner
    if (type === 'loading') {
      const spinner = document.createElement('i');
      spinner.className = 'fas fa-spinner fa-spin';
      spinner.style.marginRight = '8px';
      loginMessage.prepend(spinner);
    }
  }
}

// Highlight field with error
function highlightField(fieldId) {
  const field = document.getElementById(fieldId);
  if (field) {
    field.classList.add('error');
    field.addEventListener('input', function removeHighlight() {
      field.classList.remove('error');
      field.removeEventListener('input', removeHighlight);
    });
  }
}

// Reset all field error highlights
function resetFieldHighlights() {
  const fields = document.querySelectorAll('#loginForm input');
  fields.forEach(field => {
    field.classList.remove('error');
  });
}
        