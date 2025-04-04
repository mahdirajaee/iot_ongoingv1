/**
 * charts.js - Chart visualization for Smart IoT Bolt Dashboard
 * 
 * This file has been updated to work with the microservice architecture
 * using data from MQTT and REST APIs
 */

const Charts = (function() {
  'use strict';
  
  // Store chart instances
  const chartInstances = {};
  
  // Max data points to show in realtime charts
  const maxDataPoints = 20;
  
  // Initialize charts
  function init() {
    const temperatureChartContainer = document.getElementById('temperatureChart');
    const pressureChartContainer = document.getElementById('pressureChart');
    
    if (temperatureChartContainer) {
      chartInstances.temperature = initTemperatureChart();
    }
    
    if (pressureChartContainer) {
      chartInstances.pressure = initPressureChart();
    }
    
    // Initialize additional charts if we're on those sections
    if (document.getElementById('performanceChart')) {
      initPerformanceChart();
    }
    
    if (document.getElementById('comparisonChart')) {
      initComparisonChart();
    }
    
    if (document.getElementById('anomalyChart')) {
      initAnomalyChart();
    }
    
    if (document.getElementById('alertsTimelineChart')) {
      initAlertsTimelineChart();
    }

    if (document.getElementById('failurePredictionChart')) {
      initFailurePredictionChart();
    }

    if (document.getElementById('maintenanceForecastChart')) {
      initMaintenanceForecastChart();
    }
  }
  
  // Initialize temperature chart
  function initTemperatureChart() {
    const ctx = document.getElementById('temperatureChart').getContext('2d');
    
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(239, 68, 68, 0.6)');
    gradient.addColorStop(1, 'rgba(239, 68, 68, 0.1)');
    
    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: 'Temperature (°C)',
          data: [],
          backgroundColor: gradient,
          borderColor: '#ef4444',
          borderWidth: 2,
          pointBackgroundColor: '#ef4444',
          pointBorderColor: '#fff',
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.3,
          fill: true
        }]
      },
      options: getCommonChartOptions('temperature')
    });
  }
  
  // Initialize pressure chart
  function initPressureChart() {
    const ctx = document.getElementById('pressureChart').getContext('2d');
    
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.6)');
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0.1)');
    
    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: 'Pressure (kPa)',
          data: [],
          backgroundColor: gradient,
          borderColor: '#3b82f6',
          borderWidth: 2,
          pointBackgroundColor: '#3b82f6',
          pointBorderColor: '#fff',
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.3,
          fill: true
        }]
      },
      options: getCommonChartOptions('pressure')
    });
  }
  
  // Add a single data point to temperature chart (for real-time updates)
  function addTemperaturePoint(label, value) {
    if (!chartInstances.temperature) return;
    
    // Add new data
    chartInstances.temperature.data.labels.push(label);
    chartInstances.temperature.data.datasets[0].data.push(value);
    
    // Remove old data if we have more than maxDataPoints
    if (chartInstances.temperature.data.labels.length > maxDataPoints) {
      chartInstances.temperature.data.labels.shift();
      chartInstances.temperature.data.datasets[0].data.shift();
    }
    
    // Update chart
    chartInstances.temperature.update();
  }
  
  // Add a single data point to pressure chart (for real-time updates)
  function addPressurePoint(label, value) {
    if (!chartInstances.pressure) return;
    
    // Add new data
    chartInstances.pressure.data.labels.push(label);
    chartInstances.pressure.data.datasets[0].data.push(value);
    
    // Remove old data if we have more than maxDataPoints
    if (chartInstances.pressure.data.labels.length > maxDataPoints) {
      chartInstances.pressure.data.labels.shift();
      chartInstances.pressure.data.datasets[0].data.shift();
    }
    
    // Update chart
    chartInstances.pressure.update();
  }
  
  // Update temperature chart with historical data
  function updateTemperatureChartWithHistorical(timestamps, values) {
    if (!chartInstances.temperature) return;
    
    // Format timestamps to readable labels
    const labels = timestamps.map(ts => {
      if (typeof moment !== 'undefined') {
        return moment(ts).format('HH:mm');
      }
      return new Date(ts).toLocaleTimeString();
    });
    
    // Update chart data
    chartInstances.temperature.data.labels = labels;
    chartInstances.temperature.data.datasets[0].data = values;
    
    // Update chart
    chartInstances.temperature.update();
  }
  
  // Update pressure chart with historical data
  function updatePressureChartWithHistorical(timestamps, values) {
    if (!chartInstances.pressure) return;
    
    // Format timestamps to readable labels
    const labels = timestamps.map(ts => {
      if (typeof moment !== 'undefined') {
        return moment(ts).format('HH:mm');
      }
      return new Date(ts).toLocaleTimeString();
    });
    
    // Update chart data
    chartInstances.pressure.data.labels = labels;
    chartInstances.pressure.data.datasets[0].data = values;
    
    // Update chart
    chartInstances.pressure.update();
  }
  
  // Initialize performance chart for Analytics section
  function initPerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return null;
    
    // Generate mock data
    const labels = Array.from({length: 12}, (_, i) => {
      const date = new Date();
      date.setMonth(date.getMonth() - (11 - i));
      return date.toLocaleString('default', { month: 'short' });
    });
    
    const data = Array.from({length: 12}, () => 70 + Math.random() * 25);
    
    // Create chart
    if (chartInstances.performance) {
      chartInstances.performance.destroy();
    }
    
    chartInstances.performance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Temperature Trend (°C)',
          data: data,
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4,
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
            min: 60,
            max: 100,
            ticks: {
              color: '#64748b'
            },
            grid: {
              color: 'rgba(203, 213, 225, 0.3)'
            }
          },
          x: {
            ticks: {
              color: '#64748b'
            },
            grid: {
              display: false
            }
          }
        }
      }
    });
    
    return chartInstances.performance;
  }
  
  // Initialize comparison chart for Analytics section
  function initComparisonChart() {
    // Implementation similar to the original but with updated options
    const ctx = document.getElementById('comparisonChart');
    if (!ctx) return null;
    
    // Generate mock data
    const data = {
      labels: ['Section A', 'Section B', 'Section C'],
      datasets: [{
        label: 'Efficiency (%)',
        data: [
          80 + Math.random() * 15,
          75 + Math.random() * 15,
          85 + Math.random() * 10
        ],
        backgroundColor: [
          'rgba(59, 130, 246, 0.7)',
          'rgba(99, 102, 241, 0.7)',
          'rgba(16, 185, 129, 0.7)'
        ],
        borderWidth: 0
      }]
    };
    
    // Create chart
    if (chartInstances.comparison) {
      chartInstances.comparison.destroy();
    }
    
    chartInstances.comparison = new Chart(ctx, {
      type: 'bar',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            min: 70,
            max: 100,
            ticks: {
              color: '#64748b'
            },
            grid: {
              color: 'rgba(203, 213, 225, 0.3)'
            }
          },
          x: {
            ticks: {
              color: '#64748b'
            },
            grid: {
              display: false
            }
          }
        }
      }
    });
    
    return chartInstances.comparison;
  }
  
  // Initialize anomaly detection chart for Analytics section
  function initAnomalyChart() {
    // Implementation similar to the original but with updated options
    const ctx = document.getElementById('anomalyChart');
    if (!ctx) return null;
    
    // Generate mock data for 30 days
    const labels = Array.from({length: 30}, (_, i) => `Day ${i + 1}`);
    
    // Normal data with a few anomalies
    const baseData = Array.from({length: 30}, () => 80 + Math.random() * 10);
    
    // Add a few anomalies
    baseData[5] = 60 + Math.random() * 5;
    baseData[12] = 95 + Math.random() * 5;
    baseData[21] = 60 + Math.random() * 5;
    
    // Create datasets
    const normalData = [...baseData];
    const anomalyData = Array(30).fill(null);
    
    // Mark anomalies
    [5, 12, 21].forEach(i => {
      anomalyData[i] = baseData[i];
      normalData[i] = null;
    });
    
    // Create chart
    if (chartInstances.anomaly) {
      chartInstances.anomaly.destroy();
    }
    
    chartInstances.anomaly = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Normal Readings',
            data: normalData,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4,
            fill: true,
            pointRadius: 3
          },
          {
            label: 'Anomalies Detected',
            data: anomalyData,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            tension: 0,
            fill: false,
            pointRadius: 6,
            pointBackgroundColor: '#ef4444'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              color: '#fff'
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            min: 50,
            max: 110,
            ticks: {
              color: '#64748b'
            },
            grid: {
              color: 'rgba(203, 213, 225, 0.3)'
            }
          },
          x: {
            ticks: {
              color: '#64748b'
            },
            grid: {
              display: false
            }
          }
        }
      }
    });
    
    return chartInstances.anomaly;
  }
  
  // Initialize alerts timeline chart for Alerts section
  function initAlertsTimelineChart() {
    // Implementation similar to the original but with updated options
    const ctx = document.getElementById('alertsTimelineChart');
    if (!ctx) return null;
    
    // Generate mock data for 30 days
    const labels = Array.from({length: 30}, (_, i) => `Day ${i + 1}`);
    
    // Generate random alert counts
    const criticalData = Array.from({length: 30}, () => Math.floor(Math.random() * 3));
    const warningData = Array.from({length: 30}, () => Math.floor(Math.random() * 5));
    const infoData = Array.from({length: 30}, () => Math.floor(Math.random() * 8));
    
    // Create chart
    if (chartInstances.alertsTimeline) {
      chartInstances.alertsTimeline.destroy();
    }
    
    chartInstances.alertsTimeline = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Critical Alerts',
            data: criticalData,
            backgroundColor: '#ef4444'
          },
          {
            label: 'Warning Alerts',
            data: warningData,
            backgroundColor: '#f59e0b'
          },
          {
            label: 'Info Alerts',
            data: infoData,
            backgroundColor: '#3b82f6'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              color: '#fff'
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            stacked: true,
            ticks: {
              color: '#64748b'
            },
            grid: {
              color: 'rgba(203, 213, 225, 0.3)'
            }
          },
          x: {
            stacked: true,
            ticks: {
              color: '#64748b'
            },
            grid: {
              display: false
            }
          }
        }
      }
    });
    
    return chartInstances.alertsTimeline;
  }
  
  // Initialize failure prediction chart for Analytics section
  function initFailurePredictionChart() {
    // Implementation similar to the original but with updated options
    const ctx = document.getElementById('failurePredictionChart');
    if (!ctx) return null;
    
    // Generate mock data for next 12 weeks
    const labels = Array.from({length: 12}, (_, i) => `Week ${i + 1}`);
    
    // Prediction data with confidence intervals
    const predictedFailures = [0.2, 0.3, 0.4, 0.6, 0.8, 1.2, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0];
    const upperBound = predictedFailures.map(v => v + v * 0.3);
    const lowerBound = predictedFailures.map(v => Math.max(0, v - v * 0.3));
    
    // Create chart
    if (chartInstances.failurePrediction) {
      chartInstances.failurePrediction.destroy();
    }
    
    chartInstances.failurePrediction = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Predicted Failures',
            data: predictedFailures,
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            tension: 0.4,
            fill: false,
            pointRadius: 4
          },
          {
            label: 'Upper Bound (70% Confidence)',
            data: upperBound,
            borderColor: 'rgba(245, 158, 11, 0.3)',
            backgroundColor: 'transparent',
            tension: 0.4,
            fill: false,
            pointRadius: 0,
            borderDash: [5, 5]
          },
          {
            label: 'Lower Bound (70% Confidence)',
            data: lowerBound,
            borderColor: 'rgba(245, 158, 11, 0.3)',
            backgroundColor: 'transparent',
            tension: 0.4,
            fill: '-1',
            pointRadius: 0,
            borderDash: [5, 5]
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              color: '#fff'
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Predicted Component Failures',
              color: '#fff'
            },
            ticks: {
              color: '#64748b'
            },
            grid: {
              color: 'rgba(203, 213, 225, 0.3)'
            }
          },
          x: {
            ticks: {
              color: '#64748b'
            },
            grid: {
              display: false
            }
          }
        }
      }
    });
    
    return chartInstances.failurePrediction;
  }
  
  // Initialize maintenance forecast chart for Analytics section
  function initMaintenanceForecastChart() {
    // Implementation similar to the original but with updated options
    const ctx = document.getElementById('maintenanceForecastChart');
    if (!ctx) return null;
    
    // Generate mock data for equipment types
    const data = {
      labels: ['Valves', 'Sensors', 'Bolts', 'Controllers'],
      datasets: [
        {
          label: 'Due in 30 Days',
          data: [4, 7, 2, 1],
          backgroundColor: '#ef4444'
        },
        {
          label: 'Due in 60 Days',
          data: [6, 12, 5, 3],
          backgroundColor: '#f59e0b'
        },
        {
          label: 'Due in 90 Days',
          data: [10, 15, 8, 4],
          backgroundColor: '#3b82f6'
        }
      ]
    };
    
    // Create chart
    if (chartInstances.maintenanceForecast) {
      chartInstances.maintenanceForecast.destroy();
    }
    
    chartInstances.maintenanceForecast = new Chart(ctx, {
      type: 'bar',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              color: '#fff'
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Number of Components',
              color: '#fff'
            },
            ticks: {
              color: '#64748b'
            },
            grid: {
              color: 'rgba(203, 213, 225, 0.3)'
            }
          },
          x: {
            ticks: {
              color: '#64748b'
            },
            grid: {
              display: false
            }
          }
        }
      }
    });
    
    return chartInstances.maintenanceForecast;
  }
  
  // Initialize sensor history chart for Sensor Details modal
  function initSensorHistoryChart(sensor) {
    if (!sensor) return null;
    
    const ctx = document.getElementById('sensorHistoryChart');
    if (!ctx) return null;
    
    // Generate mock historical data
    const labels = Array.from({length: 24}, (_, i) => `${(23-i).toString().padStart(2, '0')}:00`).reverse();
    
    // Generate data based on sensor type
    let data;
    let label;
    let color;
    
    if (sensor.type === 'temperature') {
      data = Array.from({length: 24}, () => Math.floor(75 + Math.random() * 15));
      label = 'Temperature (°C)';
      color = '#ef4444';
    } else {
      data = Array.from({length: 24}, () => Math.floor(1100 + Math.random() * 200));
      label = 'Pressure (kPa)';
      color = '#3b82f6';
    }
    
    // Create chart
    if (chartInstances.sensorHistory) {
      chartInstances.sensorHistory.destroy();
    }
    
    chartInstances.sensorHistory = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: label,
          data: data,
          borderColor: color,
          backgroundColor: `${color}20`,
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              color: '#fff'
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false
          },
          title: {
            display: true,
            text: `24-Hour History for ${sensor.id}`,
            font: {
              size: 16
            },
            color: '#fff'
          }
        },
        scales: {
          y: {
            ticks: {
              color: '#64748b'
            },
            grid: {
              color: 'rgba(203, 213, 225, 0.3)'
            }
          },
          x: {
            ticks: {
              color: '#64748b'
            },
            grid: {
              display: false
            }
          }
        }
      }
    });
    
    return chartInstances.sensorHistory;
  }
  
  // Get common chart options to reduce redundancy
  function getCommonChartOptions(type) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(15, 23, 42, 0.8)',
          padding: 12,
          titleFont: {
            size: 14,
            weight: 'bold'
          },
          bodyFont: {
            size: 13
          },
          displayColors: false,
          callbacks: {
            title: function(context) {
              return context[0].dataset.label;
            },
            label: function(context) {
              const unit = type === 'temperature' ? '°C' : ' kPa';
              return `${context.parsed.y}${unit} at ${context.label}`;
            }
          }
        },
        legend: {
          display: false
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          },
          ticks: {
            font: {
              size: 11
            },
            color: '#64748b'
          }
        },
        y: {
          beginAtZero: false,
          grid: {
            color: 'rgba(203, 213, 225, 0.3)'
          },
          ticks: {
            font: {
              size: 11
            },
            color: '#64748b',
            callback: function(value) {
              return value + (type === 'temperature' ? '°C' : ' kPa');
            }
          }
        }
      },
      interaction: {
        intersect: false,
        mode: 'index'
      },
      elements: {
        line: {
          tension: 0.4
        }
      },
      animation: {
        duration: 1000
      }
    };
  }
  
  // Public API
  return {
    init,
    addTemperaturePoint,
    addPressurePoint,
    updateTemperatureChartWithHistorical,
    updatePressureChartWithHistorical,
    initPerformanceChart,
    initComparisonChart,
    initAnomalyChart,
    initAlertsTimelineChart,
    initFailurePredictionChart,
    initMaintenanceForecastChart,
    initSensorHistoryChart,
    getChartInstance: function(type) { return chartInstances[type]; }
  };
})();