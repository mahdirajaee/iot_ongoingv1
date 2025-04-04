# Analytics Microservice API Documentation

## Base URL

```
http://localhost:8083
```

> Note: The port `8083` is the default as defined in the `.env` file. If you've changed the port in your configuration, please adjust accordingly.

## API Endpoints

### 1. Service Information

Retrieves information about the Analytics Microservice and its available endpoints.

**Request**
- **Method**: `GET`
- **URL**: `/`

**Response**
```json
{
  "service": "Analytics Microservice",
  "status": "running",
  "endpoints": [
    "/api/predict/temperature",
    "/api/predict/pressure",
    "/api/anomalies/temperature",
    "/api/anomalies/pressure",
    "/api/anomalies/cascading",
    "/api/trigger-valve"
  ]
}
```

### 2. Temperature Prediction

Predicts future temperature values for a specified time horizon and checks if they will exceed configured thresholds.

**Request**
- **Method**: `GET`
- **URL**: `/predict_temperature`
- **Query Parameters**:
  - `hours` (optional): Number of hours ahead to predict (default: 1)

**Response**
```json
{
  "predictions": [
    {
      "timestamp": "2025-03-30T14:30:00.000Z",
      "value": 78.5,
      "exceeds_threshold": false
    },
    {
      "timestamp": "2025-03-30T14:31:00.000Z",
      "value": 79.2,
      "exceeds_threshold": false
    },
    ...
  ],
  "threshold_exceeded": false,
  "hours_ahead": 1
}
```

### 3. Pressure Prediction

Predicts future pressure values for a specified time horizon and checks if they will exceed configured thresholds.

**Request**
- **Method**: `GET`
- **URL**: `/predict_pressure`
- **Query Parameters**:
  - `hours` (optional): Number of hours ahead to predict (default: 1)

**Response**
```json
{
  "predictions": [
    {
      "timestamp": "2025-03-30T14:30:00.000Z",
      "value": 65.7,
      "exceeds_threshold": false
    },
    {
      "timestamp": "2025-03-30T14:31:00.000Z",
      "value": 66.3,
      "exceeds_threshold": false
    },
    ...
  ],
  "threshold_exceeded": false,
  "hours_ahead": 1
}
```

### 4. Temperature Anomalies

Detects anomalies in temperature readings from recent sensor data.

**Request**
- **Method**: `GET`
- **URL**: `/temperature_anomalies`

**Response**
```json
{
  "anomalies": [
    {
      "timestamp": "2025-03-30T14:15:00.000Z",
      "value": 92.3,
      "is_critical": true
    },
    {
      "timestamp": "2025-03-30T14:22:00.000Z",
      "value": 45.1,
      "is_critical": false
    }
  ],
  "count": 2,
  "critical_count": 1
}
```

### 5. Pressure Anomalies

Detects anomalies in pressure readings from recent sensor data.

**Request**
- **Method**: `GET`
- **URL**: `/pressure_anomalies`

**Response**
```json
{
  "anomalies": [
    {
      "timestamp": "2025-03-30T14:18:00.000Z",
      "value": 88.9,
      "is_critical": false
    }
  ],
  "count": 1,
  "critical_count": 0
}
```

### 6. Cascading Failures

Detects the risk of cascading failures by analyzing correlation and trends between temperature and pressure readings.

**Request**
- **Method**: `GET`
- **URL**: `/cascading_failures`

**Response**
```json
{
  "cascading_failure_risk": true,
  "automatic_action_taken": true
}
```

### 7. Trigger Valve

Triggers valve actuation by sending a command to the Control Center.

#### Using GET Method

**Request**
- **Method**: `GET`
- **URL**: `/trigger_valve`
- **Query Parameters**:
  - `action` (optional): Action to perform, either "open" or "close" (default: "close")
  - `automatic` (optional): Whether the action was triggered automatically (default: false)

**Response**
```json
{
  "success": true,
  "action": "close",
  "automatic": false,
  "message": "Valve close command sent successfully"
}
```

#### Using POST Method

**Request**
- **Method**: `POST`
- **URL**: `/trigger_valve`
- **Headers**:
  - `Content-Type: application/json`
- **Body**:
```json
{
  "action": "close",
  "automatic": false
}
```

**Response**
```json
{
  "success": true,
  "action": "close",
  "automatic": false,
  "message": "Valve close command sent successfully"
}
```

## Error Responses

All endpoints return appropriate HTTP status codes for error conditions:

- **400 Bad Request**: When request parameters are invalid
- **500 Internal Server Error**: When server-side processing fails

Error response format:
```json
{
  "message": "Error message describing the issue"
}
```

## Integration Notes

### Service Discovery

The Analytics Microservice automatically registers itself with the Resource Catalog upon startup. It provides information about its endpoints and capabilities, enabling other services to discover and interact with it dynamically.

### Alert Generation

When predictions or anomaly detections indicate potential issues, the microservice automatically:
1. Sends alerts to the Web Dashboard via REST API
2. Sends notifications to the Telegram Bot via REST API
3. Triggers automated valve actuation in critical situations

### Data Flow

1. The microservice retrieves historical data from the Time Series DB Connector
2. It processes this data to generate predictions or detect anomalies
3. Based on analysis results, it may send alerts or trigger valve actuation
4. All events and alerts are forwarded to user interfaces (Web Dashboard and Telegram Bot)