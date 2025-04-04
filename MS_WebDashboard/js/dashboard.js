/**
 * dashboard.js - Main functionality for Smart IoT Bolt Dashboard
 */

// Dashboard Controller
const Dashboard = (function() {
  'use strict';
  
  // Store service endpoints
  const serviceEndpoints = {
    'api-server': 'http://localhost:8088',
    'time-series-db': 'http://localhost:8081', // Fixed to match the actual TimeSeriesDBConnector port (8081)
    'analytics': 'http://localhost:8082',
    'account-manager': 'http://localhost:8083',
    'control-center': 'http://localhost:8084'
  };
  
  // Data polling timer
  let pollingTimer = null;
  const POLLING_INTERVAL = 3000; // 3 seconds
  
  // Store chart instances
  const chartInstances = {};
  
  // Alerts storage
  const alerts = [];
  
  // Initialize the dashboard
  function init() {
    // Check authentication
    if (typeof Auth !== 'undefined' && !Auth.isAuthenticated()) {
      window.location.href = 'login.html';
      return;
    }
    
    // Initialize UI
    initUI();
    
    // Initialize HTTP API connection for real-time updates
    initHTTPConnection();
    
    // Initialize charts
    if (typeof Charts !== 'undefined') {
      Charts.init();
    }
    
    // Load initial data
    loadInitialData();
    
    // If no data is available, generate some mock data for testing
    if (!pollingTimer) {
      generateMockData();
    }
  }
  
  // Initialize UI elements and event listeners
  function initUI() {
    // Set user data
    if (typeof Auth !== 'undefined') {
      const userData = Auth.getUserData();
      if (userData) {
        document.getElementById('userName').textContent = userData.name || 'User';
        document.getElementById('userAvatar').textContent = (userData.name || 'U').charAt(0) + (userData.name || '').split(' ')[1]?.charAt(0) || '';
      }
    }
    
    // Setup navigation
    setupNavigation();
    
    // Setup event listeners
    setupEventListeners();
  }
  
  // Setup navigation between sections
  function setupNavigation() {
    const navItems = document.querySelectorAll('#main-nav li');
    
    navItems.forEach(item => {
      item.addEventListener('click', function() {
        // Remove active class from all items
        navItems.forEach(i => i.classList.remove('active'));
        
        // Add active class to clicked item
        this.classList.add('active');
        
        // Get section to show
        const sectionId = this.getAttribute('data-section');
        
        // Hide all sections
        document.querySelectorAll('.dashboard-section').forEach(section => {
          section.classList.remove('active');
        });
        
        // Show selected section
        document.getElementById(sectionId).classList.add('active');
        
        // Update page title
        document.getElementById('pageTitle').textContent = `Dashboard ${sectionId.charAt(0).toUpperCase() + sectionId.slice(1)}`;
      });
    });
    
    // Mobile sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    
    if (sidebarToggle) {
      sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
        sidebarOverlay.classList.toggle('active');
      });
    }
    
    if (sidebarOverlay) {
      sidebarOverlay.addEventListener('click', () => {
        sidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
      });
    }
  }
  
  // Initialize HTTP connection for data polling
  function initHTTPConnection() {
    try {
      // Update connection status
      updateConnectionStatus('connecting', 'Connecting...');
      
      // Test API connection
      fetch(`${serviceEndpoints['api-server']}/api/data`)
        .then(response => {
          if (!response.ok) {
            throw new Error('API server connection failed');
          }
          return response.json();
        })
        .then(data => {
          console.log('API Server Connected');
          updateConnectionStatus('online', 'Connected');
          
          // Process initial data
          processAPIData(data);
          
          // Start polling for data
          startDataPolling();
          
          // Additionally, fetch pressure data from TimeSeriesDBConnector
          fetchPressureData();
          
          Utils.showToast('Connected to data API', 'success');
        })
        .catch(error => {
          console.error('API Server Error:', error);
          updateConnectionStatus('offline', 'Disconnected');
          Utils.showToast('Error connecting to data API', 'error');
          
          // For development, simulate with mock data
          setInterval(generateMockData, 5000);
        });
    } catch (error) {
      console.error('API initialization error:', error);
      updateConnectionStatus('offline', 'Disconnected');
      
      // For development, simulate with mock data
      setInterval(generateMockData, 5000);
    }
  }
  
  // Start polling for data
  function startDataPolling() {
    // Clear any existing timer
    if (pollingTimer) {
      clearInterval(pollingTimer);
    }
    
    // Start new polling timer
    pollingTimer = setInterval(() => {
      // Fetch general data
      fetch(`${serviceEndpoints['api-server']}/api/data`)
        .then(response => {
          if (!response.ok) {
            throw new Error('API server connection failed');
          }
          return response.json();
        })
        .then(data => {
          processAPIData(data);
        })
        .catch(error => {
          console.error('Data polling error:', error);
          updateConnectionStatus('offline', 'Disconnected');
          
          // Stop polling on error
          clearInterval(pollingTimer);
          pollingTimer = null;
          
          // Try to reconnect after a delay
          setTimeout(initHTTPConnection, 5000);
        });
        
      // Fetch pressure data from TimeSeriesDBConnector
      fetchPressureData();
    }, POLLING_INTERVAL);
  }
  
  // Fetch pressure data from TimeSeriesDBConnector
  function fetchPressureData() {
    fetch(`${serviceEndpoints['time-series-db']}/api/v1/data/latest?measurement=pressure`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch pressure data');
        }
        return response.json();
      })
      .then(data => {
        console.log('Pressure data received:', data);
        if (data && data.status === 'success' && data.data) {
          // Format data for pressure update
          const pressureData = {
            value: data.data.value,
            timestamp: data.data.time || new Date().toISOString(),
            location: data.data.location || 'Section B'
          };
          updatePressure(pressureData);
        }
      })
      .catch(error => {
        console.error('Error fetching pressure data:', error);
      });
  }
  
  // Process data from API
  function processAPIData(data) {
    // Process temperature data
    if (data.temperature && data.temperature.value) {
      updateTemperature(data.temperature);
    }
    
    // Process pressure data
    if (data.pressure && data.pressure.value) {
      updatePressure(data.pressure);
    }
    
    // Process valve data
    Object.values(data.valves || {}).forEach(valve => {
      if (valve && valve.id && valve.status) {
        updateValve(valve);
      }
    });
  }
  
  // Update connection status indicator
  function updateConnectionStatus(status, text) {
    const statusIndicator = document.getElementById('connectionStatus');
    const statusText = document.getElementById('statusText');
    
    if (statusIndicator) {
      statusIndicator.className = 'connection-status';
      statusIndicator.classList.add(status);
    }
    
    if (statusText) {
      statusText.textContent = text;
    }
  }
  
  // Update temperature display
  function updateTemperature(data) {
    if (!data.value) return;
    
    // Update temperature value display
    document.getElementById('tempValue').textContent = `${data.value}°C`;
    
    // Update chart if using combined chart
    updateChart('temperature', data.value);
    
    // Check for thresholds
    if (data.value > 85) {
      createAlert('critical', 'High Temperature', `Temperature reached ${data.value}°C`, data.location || 'Unknown');
    } else if (data.value > 75) {
      createAlert('warning', 'Elevated Temperature', `Temperature at ${data.value}°C`, data.location || 'Unknown');
    }
  }
  
  // Update pressure display
  function updatePressure(data) {
    if (!data.value) return;
    
    // Update pressure value display
    document.getElementById('pressureValue').textContent = `${data.value} kPa`;
    
    // Update chart if using combined chart
    updateChart('pressure', data.value);
    
    // Check for thresholds
    if (data.value > 1300) {
      createAlert('critical', 'High Pressure', `Pressure reached ${data.value} kPa`, data.location || 'Unknown');
    } else if (data.value > 1200) {
      createAlert('warning', 'Elevated Pressure', `Pressure at ${data.value} kPa`, data.location || 'Unknown');
    }
  }
  
  // Update valve status
  function updateValve(data) {
    if (!data.status) return;
    
    // Update valve status display
    document.getElementById('valveStatus').textContent = data.status === 'open' ? 'Open' : 'Closed';
    document.getElementById('valveNote').textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
    
    // Update valve in visualization
    if (data.id) {
      const valveEl = document.querySelector(`[data-valve-id="${data.id}"]`);
      if (valveEl) {
        valveEl.setAttribute('data-status', data.status);
      }
    }
    
    // Update valve controls
    updateValveControls();
    
    Utils.showToast(`Valve ${data.id || ''} is now ${data.status}`, 'info');
  }
  
  // Update the overview chart
  function updateChart(dataType, value) {
    if (!chartInstances.overview) {
      initOverviewChart();
    }
    
    // Check if we're currently displaying this data type
    const currentType = document.getElementById('chartDataSelect').value;
    if (currentType !== dataType) return;
    
    // Add new data point
    const time = new Date().toLocaleTimeString();
    const chart = chartInstances.overview;
    
    chart.data.labels.push(time);
    chart.data.datasets[0].data.push(value);
    
    // Remove old data if too many points
    if (chart.data.labels.length > 20) {
      chart.data.labels.shift();
      chart.data.datasets[0].data.shift();
    }
    
    // Update the chart
    chart.update();
  }
  
  // Initialize the overview chart
  function initOverviewChart() {
    const ctx = document.getElementById('overviewChart');
    if (!ctx) return;
    
    const selectedType = document.getElementById('chartDataSelect').value;
    const isTemp = selectedType === 'temperature';
    
    // Set up colors based on data type
    const borderColor = isTemp ? '#ef4444' : '#3b82f6';
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, isTemp ? 'rgba(239, 68, 68, 0.6)' : 'rgba(59, 130, 246, 0.6)');
    gradient.addColorStop(1, isTemp ? 'rgba(239, 68, 68, 0.1)' : 'rgba(59, 130, 246, 0.1)');
    
    // Create chart
    chartInstances.overview = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: isTemp ? 'Temperature (°C)' : 'Pressure (kPa)',
          data: [],
          backgroundColor: gradient,
          borderColor: borderColor,
          borderWidth: 2,
          pointBackgroundColor: borderColor,
          pointBorderColor: '#fff',
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.3,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            ticks: {
              color: '#64748b'
            },
            grid: {
              color: 'rgba(203, 213, 225, 0.3)'
            }
          },
          x: {
            ticks: {
              color: '#64748b',
              maxRotation: 0
            },
            grid: {
              display: false
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        },
        animation: {
          duration: 500
        }
      }
    });
  }
  
  // Update Valve Controls
  function updateValveControls() {
    const valveElements = document.querySelectorAll('.valve-point');
    
    // Count open and closed valves
    const openValves = [...valveElements].filter(el => el.getAttribute('data-status') === 'open').length;
    const totalValves = valveElements.length;
    
    // Update counts
    document.getElementById('valvesOpenCount').textContent = openValves;
    document.getElementById('valvesClosedCount').textContent = totalValves - openValves;
    
    // Update valve control table
    const valveList = document.getElementById('valveControlList');
    if (!valveList) return;
    
    valveList.innerHTML = '';
    
    valveElements.forEach(valve => {
      const valveId = valve.getAttribute('data-valve-id');
      const section = valve.closest('.pipeline-section').getAttribute('data-section');
      const status = valve.getAttribute('data-status');
      
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${valveId}</td>
        <td>${section}</td>
        <td><span class="valve-status ${status}">${status.charAt(0).toUpperCase() + status.slice(1)}</span></td>
        <td>${new Date().toLocaleTimeString()}</td>
        <td>
          <label class="switch">
            <input type="checkbox" ${status === 'open' ? 'checked' : ''} 
              onchange="Dashboard.toggleValve('${valveId}', this.checked ? 'open' : 'closed')">
            <span class="slider round"></span>
          </label>
        </td>
      `;
      
      valveList.appendChild(row);
    });
  }
  
  // Create a new alert
  function createAlert(type, title, message, location) {
    const now = new Date();
    const alert = {
      id: 'ALT-' + Math.floor(Math.random() * 1000),
      time: now.toLocaleTimeString(),
      timestamp: now.toISOString(),
      type: type,
      title: title,
      message: message,
      location: location,
      status: 'active'
    };
    
    // Add to alerts array
    alerts.unshift(alert);
    
    // Update alert counts
    updateAlertCounts();
    
    // Update recent alerts
    updateRecentAlerts();
    
    // Show toast notification
    Utils.showToast(`${title}: ${message}`, type);
    
    return alert;
  }
  
  // Update alert counts
  function updateAlertCounts() {
    const criticalCount = alerts.filter(a => a.type === 'critical' && a.status === 'active').length;
    const warningCount = alerts.filter(a => a.type === 'warning' && a.status === 'active').length;
    const infoCount = alerts.filter(a => a.type === 'info' && a.status === 'active').length;
    const resolvedToday = alerts.filter(a => 
      a.status === 'resolved' && 
      new Date(a.timestamp).toDateString() === new Date().toDateString()
    ).length;
    
    document.getElementById('criticalAlertCount').textContent = criticalCount;
    document.getElementById('warningAlertCount').textContent = warningCount;
    document.getElementById('infoAlertCount').textContent = infoCount;
    document.getElementById('resolvedAlertCount').textContent = resolvedToday;
    document.getElementById('alertCount').textContent = criticalCount + warningCount + infoCount;
    document.getElementById('alertCountBadge').textContent = criticalCount + warningCount + infoCount;
  }
  
  // Update recent alerts list
  function updateRecentAlerts() {
    const recentAlertsList = document.getElementById('recentAlertsList');
    if (!recentAlertsList) return;
    
    const recentAlerts = alerts.filter(a => a.status === 'active').slice(0, 5);
    
    recentAlertsList.innerHTML = '';
    
    if (recentAlerts.length === 0) {
      recentAlertsList.innerHTML = '<tr><td colspan="5" class="empty-state">No active alerts</td></tr>';
      return;
    }
    
    recentAlerts.forEach(alert => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${alert.time}</td>
        <td><span class="alert-type ${alert.type}">${alert.type.charAt(0).toUpperCase() + alert.type.slice(1)}</span> ${alert.title}</td>
        <td>${alert.location}</td>
        <td><span class="alert-status ${alert.status}">${alert.status}</span></td>
        <td><button class="action-btn" onclick="Dashboard.showAlertDetails('${alert.id}')">Details</button></td>
      `;
      recentAlertsList.appendChild(row);
    });
  }
  
  // Show alert details in modal
  function showAlertDetails(alertId) {
    const alert = alerts.find(a => a.id === alertId);
    if (!alert) return;
    
    // Update modal title and content
    document.getElementById('modalTitle').textContent = 'Alert Details';
    
    const content = document.getElementById('modalContent');
    content.innerHTML = `
      <div class="alert-detail-content">
        <div class="detail-row">
          <div class="detail-label">Time</div>
          <div class="detail-value">${alert.time}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Type</div>
          <div class="detail-value"><span class="alert-type ${alert.type}">${alert.type}</span> ${alert.title}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Status</div>
          <div class="detail-value"><span class="alert-status ${alert.status}">${alert.status}</span></div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Location</div>
          <div class="detail-value">${alert.location}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Description</div>
          <div class="detail-value">${alert.message}</div>
        </div>
      </div>
      <div class="alert-actions">
        ${alert.status === 'active' ? '<button class="action-btn" onclick="Dashboard.resolveAlert(\'' + alert.id + '\')">Resolve</button>' : ''}
      </div>
    `;
    
    // Show modal
    document.getElementById('generalModal').classList.add('active');
  }
  
  // Resolve an alert
  function resolveAlert(alertId) {
    const alert = alerts.find(a => a.id === alertId);
    if (!alert) return;
    
    alert.status = 'resolved';
    updateAlertCounts();
    updateRecentAlerts();
    
    // Close modal
    document.getElementById('generalModal').classList.remove('active');
    
    // Show toast
    Utils.showToast(`Alert resolved: ${alert.title}`, 'success');
  }
  
  // Toggle valve status via API
  function toggleValve(valveId, newStatus) {
    // Show loading state
    const valveElement = document.querySelector(`[data-valve="${valveId}"]`);
    if (valveElement) {
      valveElement.classList.add('loading');
    }
    
    // Call the API to change valve status
    fetch(`${serviceEndpoints['api-server']}/api/valve/${valveId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        status: newStatus
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to update valve status');
      }
      return response.json();
    })
    .then(data => {
      // Update UI with new status
      updateValve({
        id: valveId,
        status: newStatus,
        timestamp: new Date().toISOString()
      });
      
      Utils.showToast(`Valve ${valveId} ${newStatus}`, 'success');
    })
    .catch(error => {
      console.error('Error toggling valve:', error);
      Utils.showToast('Failed to update valve status', 'error');
    })
    .finally(() => {
      // Remove loading state
      if (valveElement) {
        valveElement.classList.remove('loading');
      }
    });
  }
  
  // Load initial data
  function loadInitialData() {
    // For this simplified version, we'll just generate mock data
    updateAlertCounts();
    updateRecentAlerts();
    updateValveControls();
    initOverviewChart();
  }
  
  // Set up event listeners
  function setupEventListeners() {
    // Chart type selector
    const chartDataSelect = document.getElementById('chartDataSelect');
    if (chartDataSelect) {
      chartDataSelect.addEventListener('change', function() {
        if (chartInstances.overview) {
          chartInstances.overview.destroy();
        }
        initOverviewChart();
      });
    }
    
    // Refresh buttons
    const refreshButtons = document.querySelectorAll('.refresh-btn');
    refreshButtons.forEach(btn => {
      btn.addEventListener('click', function() {
        const section = this.closest('.dashboard-section').id;
        refreshSection(section);
      });
    });
    
    // Modal close button
    const closeModalBtn = document.getElementById('closeModal');
    if (closeModalBtn) {
      closeModalBtn.addEventListener('click', function() {
        document.getElementById('generalModal').classList.remove('active');
      });
    }
    
    // Notification panel toggle
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationPanel = document.getElementById('notificationPanel');
    const closeNotifications = document.getElementById('closeNotifications');
    
    if (notificationBtn && notificationPanel) {
      notificationBtn.addEventListener('click', function() {
        notificationPanel.classList.toggle('active');
      });
    }
    
    if (closeNotifications) {
      closeNotifications.addEventListener('click', function() {
        notificationPanel.classList.remove('active');
      });
    }
    
    // User menu
    const userMenuBtn = document.getElementById('userMenuBtn');
    if (userMenuBtn) {
      userMenuBtn.addEventListener('click', function() {
        this.parentElement.classList.toggle('active');
      });
    }
    
    // Logout buttons
    document.querySelectorAll('#logoutBtn, #userLogoutBtn').forEach(btn => {
      if (btn) {
        btn.addEventListener('click', function(e) {
          e.preventDefault();
          if (typeof Auth !== 'undefined') {
            Auth.logout();
          }
          window.location.href = 'login.html';
        });
      }
    });
    
    // Add automation rule
    const addRuleBtn = document.getElementById('addRuleBtn');
    if (addRuleBtn) {
      addRuleBtn.addEventListener('click', function() {
        showAddRuleModal();
      });
    }
  }
  
  // Show add rule modal
  function showAddRuleModal() {
    document.getElementById('modalTitle').textContent = 'Add Automation Rule';
    
    const content = document.getElementById('modalContent');
    content.innerHTML = `
      <form id="newRuleForm">
        <div class="form-group">
          <label for="conditionType">Condition Type</label>
          <select id="conditionType">
            <option value="temperature">Temperature</option>
            <option value="pressure">Pressure</option>
          </select>
        </div>
        <div class="form-group">
          <label for="conditionOperator">Operator</label>
          <select id="conditionOperator">
            <option value="gt">Greater Than</option>
            <option value="lt">Less Than</option>
          </select>
        </div>
        <div class="form-group">
          <label for="conditionValue">Value</label>
          <input type="number" id="conditionValue" required placeholder="Enter value">
        </div>
        <div class="form-group">
          <label for="actionType">Action</label>
          <select id="actionType">
            <option value="openValve">Open Valve</option>
            <option value="closeValve">Close Valve</option>
            <option value="notify">Send Notification</option>
          </select>
        </div>
        <div class="form-group">
          <label for="actionTarget">Target</label>
          <select id="actionTarget">
            <option value="VA1">Valve A1</option>
            <option value="VB1">Valve B1</option>
            <option value="VC1">Valve C1</option>
          </select>
        </div>
        <div class="form-group">
          <button type="submit" class="btn-primary">Add Rule</button>
        </div>
      </form>
    `;
    
    // Show modal
    document.getElementById('generalModal').classList.add('active');
    
    // Add event listener for form submission
    document.getElementById('newRuleForm').addEventListener('submit', function(e) {
      e.preventDefault();
      
      const conditionType = document.getElementById('conditionType').value;
      const conditionOperator = document.getElementById('conditionOperator').value;
      const conditionValue = document.getElementById('conditionValue').value;
      const actionType = document.getElementById('actionType').value;
      const actionTarget = document.getElementById('actionTarget').value;
      
      addAutomationRule(conditionType, conditionOperator, conditionValue, actionType, actionTarget);
      
      // Close modal
      document.getElementById('generalModal').classList.remove('active');
    });
  }
  
  // Add automation rule
  function addAutomationRule(conditionType, operator, value, actionType, target) {
    const rulesList = document.getElementById('automationRulesList');
    if (!rulesList) return;
    
    // Format condition text
    const conditionText = operator === 'gt' 
      ? `${conditionType.charAt(0).toUpperCase() + conditionType.slice(1)} > ${value}` 
      : `${conditionType.charAt(0).toUpperCase() + conditionType.slice(1)} < ${value}`;
    
    // Format action text
    let actionText = '';
    switch (actionType) {
      case 'openValve': 
        actionText = `Open valve ${target}`; 
        break;
      case 'closeValve': 
        actionText = `Close valve ${target}`; 
        break;
      case 'notify': 
        actionText = `Send notification`; 
        break;
    }
    
    // Create row
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${conditionText}</td>
      <td>${actionText}</td>
      <td><span class="rule-status active">Active</span></td>
      <td>Never</td>
      <td>
        <button class="action-btn toggle-rule">
          <i class="fas fa-toggle-on"></i> Disable
        </button>
        <button class="action-btn delete-rule">
          <i class="fas fa-trash"></i>
        </button>
      </td>
    `;
    
    // Add row
    rulesList.appendChild(row);
    
    // Add event listeners
    row.querySelector('.toggle-rule').addEventListener('click', function() {
      const isActive = this.innerHTML.includes('Disable');
      if (isActive) {
        this.innerHTML = '<i class="fas fa-toggle-off"></i> Enable';
        row.querySelector('.rule-status').textContent = 'Inactive';
        row.querySelector('.rule-status').classList.remove('active');
        row.querySelector('.rule-status').classList.add('inactive');
      } else {
        this.innerHTML = '<i class="fas fa-toggle-on"></i> Disable';
        row.querySelector('.rule-status').textContent = 'Active';
        row.querySelector('.rule-status').classList.remove('inactive');
        row.querySelector('.rule-status').classList.add('active');
      }
    });
    
    row.querySelector('.delete-rule').addEventListener('click', function() {
      row.remove();
    });
    
    // Show success toast
    Utils.showToast(`Automation rule added successfully`, 'success');
  }
  
  // Refresh a section
  function refreshSection(section) {
    // In a real application, we would fetch new data
    // For this simplified version, we'll just show a toast
    Utils.showToast(`Refreshing ${section} data...`, 'info');
    
    setTimeout(() => {
      Utils.showToast(`${section.charAt(0).toUpperCase() + section.slice(1)} data updated`, 'success');
    }, 1000);
  }
  
  // Generate mock data when API is not available
  function generateMockData() {
    // Temperature
    const temp = 70 + Math.random() * 20;
    updateTemperature({
      value: Math.round(temp * 10) / 10,
      timestamp: new Date().toISOString(),
      location: 'Section A'
    });
    
    // Pressure
    const pressure = 1000 + Math.random() * 300;
    updatePressure({
      value: Math.round(pressure),
      timestamp: new Date().toISOString(),
      location: 'Section B'
    });
    
    // Occasionally toggle a valve
    if (Math.random() > 0.8) {
      const valves = ['VA1', 'VB1', 'VC1'];
      const randomValve = valves[Math.floor(Math.random() * valves.length)];
      const status = Math.random() > 0.5 ? 'open' : 'closed';
      
      updateValve({
        id: randomValve,
        status: status,
        timestamp: new Date().toISOString()
      });
    }
    
    // Occasionally generate an alert
    if (Math.random() > 0.9) {
      const types = ['info', 'warning', 'critical'];
      const randomType = types[Math.floor(Math.random() * types.length)];
      const locations = ['Section A', 'Section B', 'Section C'];
      const randomLocation = locations[Math.floor(Math.random() * locations.length)];
      
      createAlert(
        randomType,
        randomType === 'critical' ? 'System Alert' : 'System Notice',
        `This is a test ${randomType} alert`,
        randomLocation
      );
    }
  }
  
  // Public interface
  return {
    init: init,
    toggleValve: toggleValve,
    showAlertDetails: showAlertDetails,
    resolveAlert: resolveAlert
  };
})();

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', Dashboard.init);