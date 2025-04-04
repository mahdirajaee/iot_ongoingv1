import os
import json
import logging
import paho.mqtt.client as mqtt
from utils.data_converter import DataConverter
from services.influxdb_service import InfluxDBService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MQTTListener:
    def __init__(self, influxdb_service):
        """
        Initialize MQTT client
        
        Args:
            influxdb_service (InfluxDBService): InfluxDB service
        """
        self.influxdb_service = influxdb_service
        self.broker = os.getenv('MQTT_BROKER', 'localhost')
        self.port = int(os.getenv('MQTT_PORT', 1883))
        self.client_id = os.getenv('MQTT_CLIENT_ID', 'timeseries_db_connector')
        self.temp_topic = os.getenv('MQTT_TEMP_TOPIC', '/sensor/temperature')
        self.pressure_topic = os.getenv('MQTT_PRESSURE_TOPIC', '/sensor/pressure')
        
        # Initialize MQTT client with protocol v5 for Python 3.13.1 compatibility
        self.client = mqtt.Client(
            client_id=self.client_id, 
            protocol=mqtt.MQTTv5,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2  # Required parameter for Paho-MQTT 2.2.1
        )
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.broker, self.port, 60)
            logger.info(f"Connected to MQTT broker at {self.broker}:{self.port}")
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
            
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Disconnected from MQTT broker")
        
    def on_connect(self, client, userdata, flags, rc, properties=None):
        """
        Callback when connected to MQTT broker
        
        Subscribe to sensor topics
        
        Args:
            client: MQTT client instance
            userdata: User data
            flags: Connection flags
            rc: Result code
            properties: Properties (for MQTTv5)
        """
        if rc == 0:
            logger.info("Successfully connected to MQTT broker")
            # Subscribe to topics
            self.client.subscribe(self.temp_topic)
            logger.info(f"Subscribed to {self.temp_topic}")
            self.client.subscribe(self.pressure_topic)
            logger.info(f"Subscribed to {self.pressure_topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker with code {rc}")
            
    def on_message(self, client, userdata, msg):
        """
        Callback when message received from MQTT
        
        Process and store message in InfluxDB
        """
        try:
            logger.info(f"Received message on topic {msg.topic}")
            
            # Convert MQTT message to InfluxDB format
            point = DataConverter.mqtt_to_influxdb(msg.topic, msg.payload)
            
            if point:
                # Store in InfluxDB
                success = self.influxdb_service.write_point(point)
                if success:
                    logger.info(f"Successfully stored data for {point['measurement']} from {point['tags']['sensor_id']}")
                else:
                    logger.error("Failed to store data in InfluxDB")
            else:
                logger.error("Failed to convert MQTT message to InfluxDB format")
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")