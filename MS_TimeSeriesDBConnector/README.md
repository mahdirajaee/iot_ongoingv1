# Time Series DB Connector

A microservice for connecting IoT sensor data to InfluxDB time series database.

## Python 3.13.1 Compatibility

This project has been updated to run with Python 3.13.1, which includes:
- Compatibility patches for removed modules (`cgi`)
- Updated MQTT client for MQTTv5
- Enhanced datetime handling for Python 3.13.1
- Improved error handling and type checking

## Installation

1. Create a Python 3.13.1 virtual environment:
```bash
python3.13 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables by creating a `.env` file:
```
# InfluxDB Configuration
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your_token
INFLUXDB_ORG=your_org
INFLUXDB_BUCKET=your_bucket

# MQTT Configuration
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_CLIENT_ID=timeseries_db_connector
MQTT_TEMP_TOPIC=/sensor/temperature
MQTT_PRESSURE_TOPIC=/sensor/pressure

# Service Configuration
HOST=0.0.0.0
PORT=8081
SERVICE_NAME=TimeSeriesDBConnector
SERVICE_TYPE=database
CATALOG_URL=http://localhost:8080
```

## Running the Service

To start the service:
```bash
python main.py
```

The service will:
1. Connect to InfluxDB
2. Subscribe to MQTT topics for sensor data
3. Start a REST API server on the configured port
4. Register itself with the Resource Catalog (if configured)

## API Endpoints

- `GET /api/v1/data/temperature` - Get temperature data
- `GET /api/v1/data/pressure` - Get pressure data
- `GET /api/v1/data/latest?measurement=temperature` - Get latest temperature/pressure reading

## Dependencies

- CherryPy: Web framework
- Paho-MQTT: MQTT client
- InfluxDB Client: Time series database client
- Requests: HTTP client
- Python-dotenv: Environment variable management 