import json
import paho.mqtt.client as mqtt
import os
import time
import logging

class MQTTService:
    def __init__(self, actuator_service):
        self.client = None
        self.broker_host = os.getenv("MQTT_BROKER_HOST", "localhost")
        self.broker_port = int(os.getenv("MQTT_BROKER_PORT", 1883))
        self.client_id = os.getenv("MQTT_CLIENT_ID", "raspberry_pi_connector")
        self.topic_temperature = os.getenv("MQTT_TOPIC_TEMPERATURE", "/sensor/temperature")
        self.topic_pressure = os.getenv("MQTT_TOPIC_PRESSURE", "/sensor/pressure")
        self.topic_valve = os.getenv("MQTT_TOPIC_VALVE", "/actuator/valve")
        self.actuator_service = actuator_service
        self.setup_client()

    def setup_client(self):
        # Updated to support Python 3.13+ with required callback_api_version parameter
        import sys
        if sys.version_info >= (3, 13):
            # For Python 3.13+, use VERSION2 callback API
            self.client = mqtt.Client(
                client_id=self.client_id,
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2
            )
        else:
            # For older Python versions, use the original initialization
            self.client = mqtt.Client(client_id=self.client_id)
            
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def connect(self):
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            logging.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to MQTT broker: {e}")
            return False

    def disconnect(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logging.info("Disconnected from MQTT broker")

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """
        Callback for when the client connects to the broker.
        The properties parameter is used with MQTT v5 only (Python 3.13+).
        """
        if rc == 0:
            logging.info("Connected to MQTT broker")
            self.client.subscribe(self.topic_valve)
            logging.info(f"Subscribed to {self.topic_valve}")
        else:
            logging.error(f"Failed to connect to MQTT broker with result code {rc}")
            
    def on_disconnect(self, client, userdata, rc, properties=None):
        """
        Callback for when the client disconnects from the broker.
        The properties parameter is used with MQTT v5 only (Python 3.13+).
        """
        if rc != 0:
            logging.warning(f"Unexpected disconnection from MQTT broker with result code {rc}")
            time.sleep(5)
            self.connect()

    def on_message(self, client, userdata, msg, properties=None):
        """
        Callback for when a message is received from the broker.
        The properties parameter is used with MQTT v5 only (Python 3.13+).
        """
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            if topic == self.topic_valve:
                if "command" in payload:
                    command = payload["command"]
                    self.actuator_service.set_valve_state(command)
                    logging.info(f"Received valve command: {command}")
        except Exception as e:
            logging.error(f"Error processing MQTT message: {e}")

    def publish_temperature(self, temperature, timestamp):
        payload = {
            "value": temperature,
            "unit": "Celsius",
            "timestamp": timestamp,
            "device_id": self.client_id
        }
        self.publish(self.topic_temperature, payload)

    def publish_pressure(self, pressure, timestamp):
        payload = {
            "value": pressure,
            "unit": "PSI",
            "timestamp": timestamp,
            "device_id": self.client_id
        }
        self.publish(self.topic_pressure, payload)

    def publish(self, topic, payload):
        try:
            result = self.client.publish(topic, json.dumps(payload), qos=1)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logging.error(f"Failed to publish to {topic}: {mqtt.error_string(result.rc)}")
            else:
                logging.debug(f"Published to {topic}: {payload}")
        except Exception as e:
            logging.error(f"Error publishing to MQTT: {e}")