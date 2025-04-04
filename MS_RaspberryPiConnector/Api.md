# Raspberry Pi Connector API Endpoints

## Base URL
```
http://{host}:{port}
```
Default port: `8081`

## GET /api/sensors
Retrieves current temperature and pressure readings.

### Request
```http
GET /api/sensors HTTP/1.1
Host: localhost:8081
Content-Type: application/json
```

### Response
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "temperature": 72.35,
    "pressure": 98.76,
    "timestamp": "2025-03-30T14:22:45.123456"
}
```

| Field | Type | Description |
|-------|------|-------------|
| temperature | Float | Current temperature in Celsius |
| pressure | Float | Current pressure in PSI |
| timestamp | String | ISO 8601 formatted timestamp |

## GET /api/actuator/valve
Retrieves the current valve state.

### Request
```http
GET /api/actuator/valve HTTP/1.1
Host: localhost:8081
Content-Type: application/json
```

### Response
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "state": "closed",
    "timestamp": "2025-03-30T14:20:30.123456"
}
```

| Field | Type | Description |
|-------|------|-------------|
| state | String | Current valve state ("open" or "closed") |
| timestamp | String | ISO 8601 formatted timestamp of last state change |

## POST /api/actuator/valve
Sets the valve to a specified state.

### Request
```http
POST /api/actuator/valve HTTP/1.1
Host: localhost:8081
Content-Type: application/json

{
    "state": "open"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| state | String | Yes | Desired valve state ("open" or "closed") |

### Success Response
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "success": true
}
```

### Error Response
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "message": "Invalid valve state. Must be 'open' or 'closed'"
}
```

## MQTT Topics
In addition to REST endpoints, the Raspberry Pi Connector also communicates via MQTT:

### Publishing Topics
- `/sensor/temperature` - Temperature readings
- `/sensor/pressure` - Pressure readings

### Subscription Topics
- `/actuator/valve` - Valve control commands
