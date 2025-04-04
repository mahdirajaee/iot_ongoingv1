/**
 * main.js - Common utility functions for the Smart IoT Bolt Dashboard
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
  // Initialize particle background on landing page
  if (document.querySelector('.particle-background')) {
    initParticleBackground();
  }
  
  // Handle scroll events for header styling
  window.addEventListener('scroll', handleScroll);
  
  // Initialize any password toggle functionality
  const passwordToggle = document.getElementById('togglePassword');
  if (passwordToggle) {
    passwordToggle.addEventListener('click', togglePasswordVisibility);
  }
});

/**
 * Creates animated particle background for landing page
 */
function initParticleBackground() {
  const particleContainer = document.querySelector('.particle-background');
  const particleCount = 50;
  
  for (let i = 0; i < particleCount; i++) {
    const particle = document.createElement('div');
    
    // Set random properties for each particle
    const size = Math.random() * 6 + 2;
    const posX = Math.random() * 100;
    const posY = Math.random() * 100;
    const opacity = Math.random() * 0.5 + 0.1;
    const animationDuration = Math.random() * 20 + 10;
    const animationDelay = Math.random() * 5;
    
    // Apply styles
    particle.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      background-color: white;
      opacity: ${opacity};
      border-radius: 50%;
      top: ${posY}%;
      left: ${posX}%;
      animation: float ${animationDuration}s ease-in-out infinite;
      animation-delay: ${animationDelay}s;
      z-index: -1;
    `;
    
    particleContainer.appendChild(particle);
  }
  
  // Add float animation to stylesheet
  if (!document.querySelector('#particle-style')) {
    const style = document.createElement('style');
    style.id = 'particle-style';
    style.textContent = `
      @keyframes float {
        0% { transform: translateY(0) translateX(0); }
        25% { transform: translateY(-20px) translateX(10px); }
        50% { transform: translateY(0) translateX(20px); }
        75% { transform: translateY(20px) translateX(10px); }
        100% { transform: translateY(0) translateX(0); }
      }
    `;
    document.head.appendChild(style);
  }
}

/**
 * Handles scroll event to style header dynamically
 */
function handleScroll() {
  const header = document.querySelector('header');
  if (!header) return;
  
  if (window.scrollY > 50) {
    header.classList.add('scrolled');
  } else {
    header.classList.remove('scrolled');
  }
}

/**
 * Toggles password visibility
 */
function togglePasswordVisibility() {
  const passwordInput = document.getElementById('password');
  const toggleBtn = document.getElementById('togglePassword');
  
  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    toggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i>';
  } else {
    passwordInput.type = 'password';
    toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
  }
}