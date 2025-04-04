# Smart IoT Bolt Dashboard API Server

This server provides HTTP REST endpoints for the Smart IoT Bolt Dashboard to access real-time data without requiring WebSockets.

## Features

- RESTful API for accessing temperature, pressure, and valve status data
- Support for real MQTT broker connection or simulated data generation
- Valve control via HTTP API
- Configurable data generation interval
- Cross-origin resource sharing (CORS) support

## Installation

1. Install required dependencies:

```bash
pip install -r requirements.txt
```

2. If using an MQTT broker, ensure it's running on your desired host/port.

## Usage

### Without MQTT (Test Mode)

Run the server with simulated data generation:

```bash
python mqtt_http_proxy.py --no-mqtt
```

This will start the HTTP server on port 8088 and generate test data every 3 seconds.

### With MQTT

Run the server with an MQTT broker:

```bash
python mqtt_http_proxy.py
```

The server will try to connect to a local MQTT broker on port 1883.

### Command-line Options

```
--no-mqtt        Run without MQTT broker (use test data generator)
--port PORT      HTTP server port (default: 8088)
--interval SECS  Test data generation interval in seconds (default: 3.0)
```

Example:
```bash
python mqtt_http_proxy.py --no-mqtt --port 9000 --interval 5
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/data` | GET | Get all temperature, pressure, and valve data |
| `/api/temperature` | GET | Get temperature data |
| `/api/pressure` | GET | Get pressure data |
| `/api/valves` | GET | Get all valve statuses |
| `/api/valve/{valve_id}` | GET | Get status of specific valve |
| `/api/valve/{valve_id}` | POST | Update valve status (body: `{"status": "open"}` or `{"status": "closed"}`) |

## Data Format

### Temperature Data
```json
{
  "value": 75.5,
  "timestamp": "2023-07-01T12:00:00",
  "location": "Section A"
}
```

### Pressure Data
```json
{
  "value": 1100,
  "timestamp": "2023-07-01T12:00:00",
  "location": "Section B"
}
```

### Valve Data
```json
{
  "id": "VA1",
  "status": "open",
  "timestamp": "2023-07-01T12:00:00"
}
```

## Working with the Dashboard

The Smart IoT Bolt Dashboard is configured to connect to the API server at `http://localhost:8088`. If you change the server port, you'll need to update the `serviceEndpoints` configuration in the dashboard's JavaScript file.

## Running with Mosquitto MQTT Broker

If you want to use real MQTT data instead of generated data:

1. Install Mosquitto:
   ```bash
   # On macOS
   brew install mosquitto
   
   # On Ubuntu/Debian
   sudo apt-get install mosquitto
   ```

2. Create a mosquitto.conf file with WebSocket support:
   ```
   listener 1883
   protocol mqtt
   
   listener 9001
   protocol websockets
   ```

3. Start Mosquitto:
   ```bash
   mosquitto -c mosquitto.conf
   ```

4. Start the API server:
   ```bash
   python mqtt_http_proxy.py
   ``` 