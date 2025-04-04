import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from utils.data_processor import preprocess_time_series

load_dotenv()

class AnomalyService:
    def __init__(self):
        self.timeseries_connector_url = os.getenv("TIMESERIES_CONNECTOR_URL")
        self.temperature_threshold = float(os.getenv("TEMPERATURE_THRESHOLD"))
        self.pressure_threshold = float(os.getenv("PRESSURE_THRESHOLD"))
        self.web_dashboard_url = os.getenv("WEB_DASHBOARD_URL")
        self.telegram_bot_url = os.getenv("TELEGRAM_BOT_URL")
    
    def _get_recent_data(self, sensor_type, minutes=30):
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=minutes)
        
        try:
            response = requests.get(
                f"{self.timeseries_connector_url}/api/data/{sensor_type}",
                params={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                }
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting recent data: {response.text}")
                return None
        except Exception as e:
            print(f"Exception in _get_recent_data: {e}")
            return None
    
    def detect_anomalies(self, sensor_type):
        data = self._get_recent_data(sensor_type)
        if not data or len(data) < 10:
            return []
        
        df = preprocess_time_series(data, "value")
        
        model = IsolationForest(contamination=0.05, random_state=42)
        df['anomaly'] = model.fit_predict(df[['value']])
        
        anomalies = df[df['anomaly'] == -1]
        
        anomaly_data = []
        for idx, row in anomalies.iterrows():
            anomaly_data.append({
                "timestamp": idx.isoformat(),
                "value": float(row["value"]),
                "is_critical": self._is_critical_value(sensor_type, row["value"])
            })
        
        return anomaly_data
    
    def _is_critical_value(self, sensor_type, value):
        if sensor_type == "temperature":
            return value > self.temperature_threshold
        elif sensor_type == "pressure":
            return value > self.pressure_threshold
        return False
    
    def detect_cascading_failures(self):
        temp_data = self._get_recent_data("temperature")
        pressure_data = self._get_recent_data("pressure")
        
        if not temp_data or not pressure_data:
            return False
        
        temp_df = preprocess_time_series(temp_data, "value")
        pressure_df = preprocess_time_series(pressure_data, "value")
        
        merged_df = pd.merge(
            temp_df, pressure_df,
            left_index=True, right_index=True,
            suffixes=('_temp', '_pressure')
        )
        
        if len(merged_df) < 5:
            return False
        
        correlation = merged_df['value_temp'].corr(merged_df['value_pressure'])
        
        temp_increasing = merged_df['value_temp'].pct_change().mean() > 0.02
        pressure_increasing = merged_df['value_pressure'].pct_change().mean() > 0.02
        
        cascading_risk = (
            correlation > 0.7 and 
            temp_increasing and 
            pressure_increasing and
            merged_df['value_temp'].iloc[-1] > 0.8 * self.temperature_threshold and
            merged_df['value_pressure'].iloc[-1] > 0.8 * self.pressure_threshold
        )
        
        return cascading_risk
    
    def send_alert(self, alert_type, message, data=None):
        try:
            dashboard_response = requests.post(
                f"{self.web_dashboard_url}/api/alerts",
                json={
                    "type": alert_type,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "data": data
                }
            )
        except Exception as e:
            print(f"Failed to send alert to dashboard: {e}")
        
        try:
            telegram_response = requests.post(
                f"{self.telegram_bot_url}/api/alerts",
                json={
                    "type": alert_type,
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            print(f"Failed to send alert to telegram bot: {e}")