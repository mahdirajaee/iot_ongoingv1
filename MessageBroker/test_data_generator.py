#!/usr/bin/env python3
"""
Test Data Generator for Smart IoT Bolt Dashboard
This script generates random test data and injects it directly into the data store
of the CherryPy server, without requiring an MQTT broker.

Usage: Run this script alongside the mqtt_http_proxy.py with the --no-mqtt flag
"""

import time
import random
import threading
import argparse
import json
import math

# Simulated data ranges
TEMP_MIN = 65
TEMP_MAX = 95
PRESSURE_MIN = 950
PRESSURE_MAX = 1350
VALVES = ["VA1", "VB1", "VC1"]  # Valve IDs

class TestDataGenerator:
    def __init__(self, data_store):
        self.data_store = data_store
        self.running = False
        self.thread = None
    
    def start(self, interval=5.0):
        """Start generating test data at the specified interval (seconds)"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._generate_data_loop, args=(interval,))
        self.thread.daemon = True
        self.thread.start()
        print(f"Test data generator started (interval: {interval}s)")
    
    def stop(self):
        """Stop the test data generator"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        print("Test data generator stopped")
    
    def _generate_data_loop(self, interval):
        """Generate data in a loop at the specified interval"""
        while self.running:
            try:
                # Generate temperature data
                self._generate_temperature()
                
                # Generate pressure data
                self._generate_pressure()
                
                # Occasionally toggle a random valve (20% chance)
                if random.random() > 0.8:
                    self._toggle_random_valve()
                
                # Update last update timestamp
                self.data_store.last_update = time.time()
                
                # Sleep for the interval
                time.sleep(interval)
                
            except Exception as e:
                print(f"Error generating test data: {e}")
                time.sleep(1)  # Sleep briefly on error
    
    def _generate_temperature(self):
        """Generate random temperature data"""
        # Generate a value with some randomness but following a trend
        base_temp = 70 + 10 * math.sin(time.time() / 300)  # Slowly oscillating base temperature
        random_factor = random.random() * 5  # Random variation of ±5 degrees
        temp = base_temp + random_factor
        temp = max(TEMP_MIN, min(TEMP_MAX, temp))  # Ensure within limits
        
        self.data_store.temperature = {
            "value": round(temp, 1),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "location": "Section A"
        }
        
        print(f"Generated temperature: {self.data_store.temperature['value']}°F")
    
    def _generate_pressure(self):
        """Generate random pressure data"""
        # Generate a value with some randomness but following a trend
        base_pressure = 1200 + 100 * math.sin(time.time() / 400)  # Slowly oscillating base pressure
        random_factor = random.random() * 50  # Random variation of ±50 psi
        pressure = base_pressure + random_factor
        pressure = max(PRESSURE_MIN, min(PRESSURE_MAX, pressure))  # Ensure within limits
        
        self.data_store.pressure = {
            "value": round(pressure),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "location": "Section B"
        }
        
        print(f"Generated pressure: {self.data_store.pressure['value']} psi")
    
    def _toggle_random_valve(self):
        """Toggle a random valve status"""
        valve_id = random.choice(VALVES)
        current_status = "closed"
        
        # Check current status if valve exists
        if valve_id in self.data_store.valves:
            current_status = self.data_store.valves[valve_id].get("status", "closed")
        
        # Toggle status
        new_status = "open" if current_status == "closed" else "closed"
        
        # Update valve data
        self.data_store.valves[valve_id] = {
            "id": valve_id,
            "status": new_status,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        
        print(f"Toggled valve {valve_id} to {new_status}")

# Stand-alone test function
def test_generator():
    """Test the generator by printing simulated data to console"""
    class MockDataStore:
        def __init__(self):
            self.temperature = {}
            self.pressure = {}
            self.valves = {}
            self.last_update = 0
    
    data_store = MockDataStore()
    generator = TestDataGenerator(data_store)
    generator.start(interval=3.0)
    
    try:
        print("Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping test")
    finally:
        generator.stop()

if __name__ == "__main__":
    print("This script is normally imported and used by mqtt_http_proxy.py")
    print("Running as standalone will simulate data generation for testing")
    test_generator() 