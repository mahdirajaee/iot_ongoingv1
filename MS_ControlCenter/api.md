# Control Center API Documentation

## Overview

The Control Center provides two primary REST API endpoints for interacting with the system:

1. `GET /api/control/status` - Retrieves current system status
2. `POST /api/control/command` - Sends manual control commands to the valve

## API Endpoints

### 1. Get System Status

Retrieves the current system status including the latest sensor readings and valve recommendation.

**Endpoint:** `GET /api/control/status`

**Authentication:** None (Internal service communication)

**Request Parameters:** None

**Response Format:**
```json
{
  "latest_data": {
    "temperature": 75.3,
    "pressure": 142.7,
    "timestamp": "2025-03-30T17:45:23.456789"
  },
  "valve_recommendation": "OPEN"
}
```

**Response Fields:**
- `latest_data.temperature`: The most recent temperature reading (in °C)
- `latest_data.pressure`: The most recent pressure reading (in PSI)
- `latest_data.timestamp`: ISO 8601 timestamp of the last sensor update
- `valve_recommendation`: Current recommended valve state based on thresholds ("OPEN", "CLOSE", or null if within normal range)

**Status Codes:**
- `200 OK`: Request successful
- `500 Internal Server Error`: Server error occurred

### 2. Send Valve Command

Sends a manual command to operate the valve.

**Endpoint:** `POST /api/control/command`

**Authentication:** None (Should be implemented via Account Manager in production)

**Request Format:**
```json
{
  "command": "OPEN"
}
```

**Request Fields:**
- `command`: The valve operation to perform. Must be either "OPEN" or "CLOSE" (case-insensitive, will be converted to uppercase)

**Response Format:**
```json
{
  "status": "success",
  "message": "Command OPEN sent successfully"
}
```

**Status Codes:**
- `200 OK`: Command sent successfully
- `400 Bad Request`: Invalid command or missing field
- `500 Internal Server Error`: Failed to send command

## Usage Examples

### Checking System Status

**cURL Example:**
```bash
curl -X GET http://localhost:8081/api/control/status
```

### Sending a Valve Command

**cURL Example:**
```bash
curl -X POST http://localhost:8081/api/control/command \
     -H "Content-Type: application/json" \
     -d '{"command": "OPEN"}'
```

## Integration with Other Microservices

- **Web Dashboard**: Uses these endpoints to display current status and provide manual control UI
- **Telegram Bot**: Accesses these endpoints to allow remote monitoring and control
- **Control Center**: Implements these endpoints for system integration