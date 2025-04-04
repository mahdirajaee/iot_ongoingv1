/**
 * utils.js - Utility functions for Smart IoT Bolt Dashboard
 */

const Utils = (function() {
  'use strict';
  
  /**
   * Show a toast notification
   * @param {string} message - The message to display
   * @param {string} type - The type of toast (success, error, warning, info)
   * @param {number} duration - How long to show the toast (ms)
   */
  function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Add icon based on type
    let icon;
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
      case 'info':
      default:
        icon = '<i class="fas fa-info-circle"></i>';
        break;
    }
    
    // Set content
    toast.innerHTML = `
      <div class="toast-icon">${icon}</div>
      <div class="toast-message">${message}</div>
      <button class="toast-close"><i class="fas fa-times"></i></button>
    `;
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Show toast with animation
    setTimeout(() => {
      toast.classList.add('show');
    }, 10);
    
    // Setup close button
    toast.querySelector('.toast-close').addEventListener('click', () => {
      closeToast(toast);
    });
    
    // Auto close after duration
    setTimeout(() => {
      closeToast(toast);
    }, duration);
  }
  
  /**
   * Close and remove a toast notification
   * @param {Element} toast - The toast element to remove
   */
  function closeToast(toast) {
    toast.classList.remove('show');
    
    // Remove after animation completes
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }
  
  /**
   * Format a date string or timestamp
   * @param {string|number} date - The date to format
   * @param {string} format - The format to use
   * @returns {string} Formatted date string
   */
  function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
    if (typeof moment !== 'undefined') {
      return moment(date).format(format);
    }
    
    // Basic fallback if moment.js is not available
    const d = new Date(date);
    return d.toLocaleString();
  }
  
  /**
   * Format a number with specified precision
   * @param {number} value - The number to format
   * @param {number} precision - Number of decimal places
   * @returns {string} Formatted number
   */
  function formatNumber(value, precision = 1) {
    return Number(value).toFixed(precision);
  }
  
  /**
   * Safely parse JSON with error handling
   * @param {string} str - The string to parse
   * @param {*} fallback - Fallback value if parsing fails
   * @returns {*} Parsed object or fallback
   */
  function safeJSONParse(str, fallback = {}) {
    try {
      return JSON.parse(str);
    } catch (err) {
      console.error('JSON Parse Error:', err);
      return fallback;
    }
  }
  
  /**
   * Generate a random ID
   * @param {string} prefix - Prefix for the ID
   * @returns {string} Random ID
   */
  function generateId(prefix = 'id') {
    return `${prefix}-${Math.random().toString(36).substring(2, 10)}`;
  }
  
  /**
   * Debounce a function to limit how often it can be called
   * @param {Function} func - The function to debounce
   * @param {number} wait - Time to wait between calls (ms)
   * @returns {Function} Debounced function
   */
  function debounce(func, wait = 300) {
    let timeout;
    return function(...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  }
  
  /**
   * Add event listener with automatic cleanup
   * @param {Element} element - Element to attach listener to
   * @param {string} event - Event name
   * @param {Function} handler - Event handler
   */
  function addEventListenerWithCleanup(element, event, handler) {
    if (!element || !event || !handler) return;
    
    element.addEventListener(event, handler);
    
    // Return function to remove the listener
    return () => {
      element.removeEventListener(event, handler);
    };
  }
  
  /**
   * Get a query parameter from the URL
   * @param {string} name - Parameter name
   * @returns {string|null} Parameter value or null
   */
  function getQueryParam(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
  }
  
  // Public API
  return {
    showToast,
    formatDate,
    formatNumber,
    safeJSONParse,
    generateId,
    debounce,
    addEventListenerWithCleanup,
    getQueryParam
  };
})();