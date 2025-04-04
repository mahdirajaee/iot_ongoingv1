import json
import paho.mqtt.client as mqtt
import logging

class MQTTHandler:
    def __init__(self, broker_host, broker_port, client_id, on_message_callback, username=None, password=None):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.on_message_callback = on_message_callback
        self.username = username
        self.password = password
        self.client = None
        self.connected = False
        
        self.sensor_topics = ["/sensor/temperature", "/sensor/pressure"]
        self.actuator_topic = "/actuator/valve"
        
        self._setup_mqtt_client()
    
    def _setup_mqtt_client(self):
        # Explicitly set callback_api_version for paho-mqtt 2.0+
        self.client = mqtt.Client(client_id=self.client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
    
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logging.info("Connected to MQTT Broker")
            
            for topic in self.sensor_topics:
                self.client.subscribe(topic)
                logging.info(f"Subscribed to {topic}")
        else:
            logging.error(f"Failed to connect to MQTT Broker with code {rc}")
    
    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
            logging.debug(f"Received message on {msg.topic}: {payload}")
            
            if self.on_message_callback:
                self.on_message_callback(msg.topic, payload)
                
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON from message: {msg.payload}")
        except Exception as e:
            logging.error(f"Error processing message: {str(e)}")
    
    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        if rc != 0:
            logging.warning(f"Unexpected disconnection from MQTT Broker with code {rc}")
        else:
            logging.info("Disconnected from MQTT Broker")
    
    def connect(self):
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
        except Exception as e:
            logging.error(f"Failed to connect to MQTT Broker: {str(e)}")
    
    def disconnect(self):
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
    
    def publish_valve_command(self, command):
        if not self.connected:
            logging.warning("Not connected to MQTT Broker. Cannot publish command.")
            return False
        
        try:
            payload = json.dumps({"command": command})
            result = self.client.publish(self.actuator_topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logging.info(f"Published command '{command}' to {self.actuator_topic}")
                return True
            else:
                logging.error(f"Failed to publish command with code {result.rc}")
                return False
                
        except Exception as e:
            logging.error(f"Error publishing command: {str(e)}")
            return False