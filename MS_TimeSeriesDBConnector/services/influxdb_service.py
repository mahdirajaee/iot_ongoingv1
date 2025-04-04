import os
from datetime import datetime, timedelta
import logging
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import contextlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InfluxDBService:
    def __init__(self):
        """Initialize InfluxDB connection"""
        self.url = os.getenv('INFLUXDB_URL')
        self.token = os.getenv('INFLUXDB_TOKEN')
        self.org = os.getenv('INFLUXDB_ORG')
        self.bucket = os.getenv('INFLUXDB_BUCKET')
        
        self.client = None
        self.write_api = None
        self.query_api = None
        
        self.connect()
        
    def connect(self):
        """Establish connection to InfluxDB"""
        try:
            # Updated to use context manager for Python 3.13.1 compatibility
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org, timeout=30000)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
            logger.info("Successfully connected to InfluxDB")
        except Exception as e:
            logger.error(f"Error connecting to InfluxDB: {e}")
            
    def write_point(self, point):
        """
        Write data point to InfluxDB
        
        Args:
            point (dict): Data point in InfluxDB format
        
        Returns:
            bool: Success status
        """
        try:
            self.write_api.write(bucket=self.bucket, record=point)
            return True
        except Exception as e:
            logger.error(f"Error writing to InfluxDB: {e}")
            # Try to reconnect
            self.connect()
            return False
            
    def query_data(self, measurement, start_time=None, end_time=None, sensor_id=None, pipeline_id=None):
        """
        Query data from InfluxDB
        
        Args:
            measurement (str): Measurement name (temperature or pressure)
            start_time (datetime, optional): Start time for query range
            end_time (datetime, optional): End time for query range
            sensor_id (str, optional): Filter by sensor ID
            pipeline_id (str, optional): Filter by pipeline ID
            
        Returns:
            FluxTable: Query result
        """
        try:
            # Set default time range to last 24 hours if not specified
            if not start_time:
                start_time = datetime.utcnow() - timedelta(hours=24)
            if not end_time:
                end_time = datetime.utcnow()
                
            # Format datetime objects for InfluxDB query - updated for Python 3.13.1
            start_str = start_time.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
            end_str = end_time.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                
            # Build query
            query = f'from(bucket: "{self.bucket}") |> range(start: {start_str}, stop: {end_str})'
            query += f' |> filter(fn: (r) => r._measurement == "{measurement}")'
            
            # Add filters if specified
            if sensor_id:
                query += f' |> filter(fn: (r) => r.sensor_id == "{sensor_id}")'
            if pipeline_id:
                query += f' |> filter(fn: (r) => r.pipeline_id == "{pipeline_id}")'
                
            # Execute query
            result = self.query_api.query(query=query, org=self.org)
            return result
        except Exception as e:
            logger.error(f"Error querying InfluxDB: {e}")
            # Try to reconnect
            self.connect()
            return []
            
    def get_latest_reading(self, measurement, sensor_id=None, pipeline_id=None):
        """
        Get the latest reading for a specific measurement
        
        Args:
            measurement (str): Measurement name (temperature or pressure)
            sensor_id (str, optional): Filter by sensor ID
            pipeline_id (str, optional): Filter by pipeline ID
            
        Returns:
            dict: Latest reading
        """
        try:
            # Build query to get latest reading
            query = f'from(bucket: "{self.bucket}") |> range(start: -1h)'
            query += f' |> filter(fn: (r) => r._measurement == "{measurement}")'
            
            # Add filters if specified
            if sensor_id:
                query += f' |> filter(fn: (r) => r.sensor_id == "{sensor_id}")'
            if pipeline_id:
                query += f' |> filter(fn: (r) => r.pipeline_id == "{pipeline_id}")'
                
            # Get latest reading
            query += ' |> last()'
            
            # Execute query
            result = self.query_api.query(query=query, org=self.org)
            
            # Process result - updated for Python 3.13.1 compatibility
            if len(result) > 0 and len(result[0].records) > 0:
                record = result[0].records[0]
                
                # Handle time value with proper error handling
                time_value = record.get_time()
                if hasattr(time_value, 'isoformat'):
                    time_str = time_value.isoformat()
                else:
                    time_str = str(time_value)
                
                return {
                    'measurement': measurement,
                    'sensor_id': record.values.get('sensor_id', 'unknown'),
                    'pipeline_id': record.values.get('pipeline_id', 'unknown'),
                    'value': record.get_value(),
                    'time': time_str
                }
            return None
        except Exception as e:
            logger.error(f"Error getting latest reading: {e}")
            return None