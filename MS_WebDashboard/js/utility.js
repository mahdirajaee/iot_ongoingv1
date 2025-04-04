/**
 * utility.js - Common utility functions for Smart IoT Bolt Dashboard
 */

const Utils = (function() {
  'use strict';
  
  // Show toast notification
  function showToast(message, type = 'info', duration = 3000) {
    // Get or create toast container
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Set icon based on type
    let icon = '';
    switch (type) {
      case 'success':
        icon = '<i class="fas fa-check-circle"></i>';
        break;
      case 'error':
        icon = '<i class="fas fa-times-circle"></i>';
        break;
      case 'warning':
        icon = '<i class="fas fa-exclamation-triangle"></i>';
        break;
      default:
        icon = '<i class="fas fa-info-circle"></i>';
    }
    
    // Set content
    toast.innerHTML = `
      <div class="toast-icon">
        ${icon}
      </div>
      <div class="toast-content">${message}</div>
      <button class="toast-close">
        <i class="fas fa-times"></i>
      </button>
    `;
    
    // Add close button event
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
      toast.classList.add('toast-hiding');
      setTimeout(() => {
        if (toast.parentNode) {
          toast.remove();
        }
      }, 300);
    });
    
    // Add to container
    container.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
      toast.classList.add('toast-visible');
    }, 10);
    
    // Remove after duration
    setTimeout(() => {
      if (toast.parentNode) {
        toast.classList.add('toast-hiding');
        setTimeout(() => {
          if (toast.parentNode) {
            toast.remove();
          }
        }, 300);
      }
    }, duration);
  }
  
  // Format number with thousands separator
  function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }
  
  // Format date to locale string
  function formatDate(date, options) {
    const defaultOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    };
    
    return new Date(date).toLocaleDateString(undefined, options || defaultOptions);
  }
  
  // Format time to locale string
  function formatTime(date, options) {
    const defaultOptions = {
      hour: '2-digit',
      minute: '2-digit'
    };
    
    return new Date(date).toLocaleTimeString(undefined, options || defaultOptions);
  }
  
  // Format date and time together
  function formatDateTime(date, options) {
    const defaultOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    
    return new Date(date).toLocaleString(undefined, options || defaultOptions);
  }
  
  // Calculate relative time (e.g., "5 minutes ago")
  function timeAgo(date) {
    const now = new Date();
    const diffMs = now - new Date(date);
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHr = Math.floor(diffMin / 60);
    const diffDays = Math.floor(diffHr / 24);
    
    if (diffSec < 60) {
      return 'Just now';
    } else if (diffMin < 60) {
      return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
    } else if (diffHr < 24) {
      return `${diffHr} hour${diffHr > 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else {
      return formatDate(date);
    }
  }
  
  // Debounce function to limit function calls
  function debounce(func, wait, immediate) {
    let timeout;
    return function() {
      const context = this;
      const args = arguments;
      
      const later = function() {
        timeout = null;
        if (!immediate) func.apply(context, args);
      };
      
      const callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      
      if (callNow) func.apply(context, args);
    };
  }
  
  // Generate random ID
  function generateId(prefix = '') {
    return `${prefix}${Math.random().toString(36).substr(2, 9)}`;
  }
  
  // Convert CSV to JSON
  function csvToJson(csv) {
    const lines = csv.split('\n');
    const result = [];
    const headers = lines[0].split(',');
    
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i]) continue;
      
      const obj = {};
      const currentLine = lines[i].split(',');
      
      for (let j = 0; j < headers.length; j++) {
        obj[headers[j]] = currentLine[j];
      }
      
      result.push(obj);
    }
    
    return result;
  }
  
  // Download data as CSV file
  function downloadCsv(data, filename) {
    const csvContent = "data:text/csv;charset=utf-8," + data;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
  
  // Check if element is in viewport
  function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  }
  
  // Public API
  return {
    showToast,
    formatNumber,
    formatDate,
    formatTime,
    formatDateTime,
    timeAgo,
    debounce,
    generateId,
    csvToJson,
    downloadCsv,
    isInViewport
  };
})();

// Mock authentication service for demo purposes
// This would be replaced with real authentication in production
const UtilityAuth = (function() {
  'use strict';
  
  let isLoggedIn = true;
  
  const mockUser = {
    id: 'usr123',
    name: 'User',
    email: 'user@example.com',
    avatar: 'U',
    role: 'admin'
  };
  
  // Check if user is authenticated
  function isAuthenticated() {
    const token = localStorage.getItem('auth_token');
    if (!token) return false;
    
    try {
      // Check token expiration
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp > Date.now() / 1000;
    } catch (e) {
      return false;
    }
  }
  
  // Get user data
  function getUserData() {
    return mockUser;
  }
  
  // Simulate login
  function login(email, password) {
    // In a real app, this would send credentials to the account-manager microservice
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (email && password) {
          // Store a mock token
          const expiresIn = 24 * 60 * 60; // 24 hours
          const expiration = Math.floor(Date.now() / 1000) + expiresIn;
          const payload = { sub: 'usr123', exp: expiration };
          const token = `header.${btoa(JSON.stringify(payload))}.signature`;
          
          localStorage.setItem('auth_token', token);
          isLoggedIn = true;
          resolve(mockUser);
        } else {
          reject(new Error('Invalid credentials'));
        }
      }, 800);
    });
  }
  
  // Simulate logout
  function logout() {
    localStorage.removeItem('auth_token');
    isLoggedIn = false;
    window.location.href = 'login.html';
  }
  
  // Public API
  return {
    isAuthenticated,
    getUserData,
    login,
    logout
  };
})();