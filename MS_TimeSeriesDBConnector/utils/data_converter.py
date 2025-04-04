import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataConverter:
    @staticmethod
    def mqtt_to_influxdb(topic, payload):
        """
        Convert MQTT message payload to InfluxDB point format
        
        Args:
            topic (str): MQTT topic
            payload (bytes): MQTT message payload
            
        Returns:
            dict: InfluxDB point data
        """
        try:
            # Decode JSON payload - updated for Python 3.13.1 compatibility
            if isinstance(payload, bytes):
                data = json.loads(payload.decode('utf-8'))
            elif isinstance(payload, str):
                data = json.loads(payload)
            else:
                data = payload  # Assume it's already a dict
            
            # Extract sensor ID and value
            sensor_id = data.get('sensor_id', 'unknown')
            value = data.get('value')
            
            # Handle timestamp - updated for Python 3.13.1 compatibility
            timestamp = data.get('timestamp')
            if not timestamp:
                timestamp = datetime.utcnow().isoformat(timespec='milliseconds')
            
            # Determine measurement name based on topic
            if 'temperature' in topic:
                measurement = 'temperature'
            elif 'pressure' in topic:
                measurement = 'pressure'
            else:
                measurement = 'unknown'
                
            # Create InfluxDB point
            point = {
                "measurement": measurement,
                "tags": {
                    "sensor_id": sensor_id,
                    "pipeline_id": data.get('pipeline_id', 'unknown')
                },
                "time": timestamp,
                "fields": {
                    "value": float(value)
                }
            }
            
            return point
        except Exception as e:
            logger.error(f"Error converting MQTT data to InfluxDB format: {e}")
            return None
    
    @staticmethod
    def influxdb_to_json(query_result):
        """
        Convert InfluxDB query result to JSON format
        
        Args:
            query_result (FluxTable): InfluxDB query result
            
        Returns:
            list: List of measurements in JSON format
        """
        try:
            result = []
            for table in query_result:
                for record in table.records:
                    # Updated for Python 3.13.1 compatibility - handle datetime formats
                    time_value = record.get_time()
                    if hasattr(time_value, 'isoformat'):
                        time_str = time_value.isoformat()
                    else:
                        time_str = str(time_value)
                        
                    result.append({
                        'measurement': record.get_measurement(),
                        'sensor_id': record.values.get('sensor_id', 'unknown'),
                        'pipeline_id': record.values.get('pipeline_id', 'unknown'),
                        'value': record.get_value(),
                        'time': time_str
                    })
            return result
        except Exception as e:
            logger.error(f"Error converting InfluxDB data to JSON: {e}")
            return []