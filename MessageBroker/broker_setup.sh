#!/bin/bash

echo "Starting Mosquitto MQTT broker setup..."

# Update package lists
apt-get update

# Install Mosquitto broker and client tools
apt-get install -y mosquitto mosquitto-clients

# Back up the original configuration
cp /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.bak

# Create new configuration
cat > /etc/mosquitto/mosquitto.conf << EOF
# Smart IoT Bolt for Pipelines - Mosquitto Configuration

# Basic settings
listener 1883 0.0.0.0
allow_anonymous true

# Persistence settings
persistence true
persistence_location /var/lib/mosquitto/

# Logging settings
log_dest file /var/log/mosquitto/mosquitto.log
log_type all
connection_messages true

# Performance settings
max_queued_messages 1000
max_inflight_messages 20
EOF

# Create a systemd service for automatic startup
cat > /etc/systemd/system/mosquitto.service << EOF
[Unit]
Description=Mosquitto MQTT Broker
Documentation=https://mosquitto.org/
After=network.target

[Service]
Type=simple
ExecStart=/usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, restart mosquitto, enable on boot
systemctl daemon-reload
systemctl restart mosquitto
systemctl enable mosquitto

# Check if mosquitto is running
if systemctl is-active --quiet mosquitto; then
    echo "MQTT broker successfully installed and running on port 1883"
else
    echo "MQTT broker installation failed, check logs for details"
    exit 1
fi

echo "Setup complete! MQTT broker is configured and running."