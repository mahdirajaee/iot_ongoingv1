import cherrypy
import json
from datetime import datetime, timedelta
import logging
from services.influxdb_service import InfluxDBService
from utils.data_converter import DataConverter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataController:
    def __init__(self, influxdb_service):
        """
        Initialize data controller
        
        Args:
            influxdb_service (InfluxDBService): InfluxDB service
        """
        self.influxdb_service = influxdb_service
        
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        """Root endpoint"""
        return {
            "service": "Time Series DB Connector",
            "status": "running",
            "endpoints": [
                "/api/v1/data/temperature",
                "/api/v1/data/pressure",
                "/api/v1/data/latest"
            ]
        }
        
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def temperature(self, start=None, end=None, sensor_id=None, pipeline_id=None):
        """
        Get temperature data
        
        Args:
            start (str, optional): Start time (ISO format)
            end (str, optional): End time (ISO format)
            sensor_id (str, optional): Filter by sensor ID
            pipeline_id (str, optional): Filter by pipeline ID
            
        Returns:
            dict: Temperature data
        """
        try:
            # Parse time parameters - updated for Python 3.13.1 compatibility
            start_time = None
            end_time = None
            
            if start:
                try:
                    start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                except ValueError:
                    start_time = datetime.utcnow() - timedelta(hours=24)
            else:
                start_time = datetime.utcnow() - timedelta(hours=24)
                
            if end:
                try:
                    end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))
                except ValueError:
                    end_time = datetime.utcnow()
            else:
                end_time = datetime.utcnow()
            
            # Query InfluxDB
            query_result = self.influxdb_service.query_data(
                measurement="temperature",
                start_time=start_time,
                end_time=end_time,
                sensor_id=sensor_id,
                pipeline_id=pipeline_id
            )
            
            # Convert to JSON
            data = DataConverter.influxdb_to_json(query_result)
            
            return {
                "status": "success",
                "data": data,
                "count": len(data)
            }
        except Exception as e:
            logger.error(f"Error retrieving temperature data: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def pressure(self, start=None, end=None, sensor_id=None, pipeline_id=None):
        """
        Get pressure data
        
        Args:
            start (str, optional): Start time (ISO format)
            end (str, optional): End time (ISO format)
            sensor_id (str, optional): Filter by sensor ID
            pipeline_id (str, optional): Filter by pipeline ID
            
        Returns:
            dict: Pressure data
        """
        try:
            # Parse time parameters - updated for Python 3.13.1 compatibility
            start_time = None
            end_time = None
            
            if start:
                try:
                    start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                except ValueError:
                    start_time = datetime.utcnow() - timedelta(hours=24)
            else:
                start_time = datetime.utcnow() - timedelta(hours=24)
                
            if end:
                try:
                    end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))
                except ValueError:
                    end_time = datetime.utcnow()
            else:
                end_time = datetime.utcnow()
            
            # Query InfluxDB
            query_result = self.influxdb_service.query_data(
                measurement="pressure",
                start_time=start_time,
                end_time=end_time,
                sensor_id=sensor_id,
                pipeline_id=pipeline_id
            )
            
            # Convert to JSON
            data = DataConverter.influxdb_to_json(query_result)
            
            return {
                "status": "success",
                "data": data,
                "count": len(data)
            }
        except Exception as e:
            logger.error(f"Error retrieving pressure data: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def latest(self, measurement, sensor_id=None, pipeline_id=None):
        """
        Get latest reading for a measurement
        
        Args:
            measurement (str): Measurement name (temperature or pressure)
            sensor_id (str, optional): Filter by sensor ID
            pipeline_id (str, optional): Filter by pipeline ID
            
        Returns:
            dict: Latest reading
        """
        try:
            if measurement not in ['temperature', 'pressure']:
                raise ValueError("Measurement must be 'temperature' or 'pressure'")
                
            # Get latest reading
            data = self.influxdb_service.get_latest_reading(
                measurement=measurement,
                sensor_id=sensor_id,
                pipeline_id=pipeline_id
            )
            
            if data:
                return {
                    "status": "success",
                    "data": data
                }
            else:
                return {
                    "status": "error",
                    "message": f"No {measurement} data found"
                }
        except Exception as e:
            logger.error(f"Error retrieving latest {measurement}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }