import pandas as pd
import numpy as np
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from models.prediction_model import ARIMAModel, find_best_arima_params
from utils.data_processor import preprocess_time_series, check_stationarity, make_stationary

load_dotenv()

class PredictionService:
    def __init__(self):
        self.timeseries_connector_url = os.getenv("TIMESERIES_CONNECTOR_URL")
        self.temperature_model = ARIMAModel()
        self.pressure_model = ARIMAModel()
        self.temperature_threshold = float(os.getenv("TEMPERATURE_THRESHOLD"))
        self.pressure_threshold = float(os.getenv("PRESSURE_THRESHOLD"))
    
    def _get_historical_data(self, sensor_type, hours=12):
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
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
                print(f"Error getting historical data: {response.text}")
                return None
        except Exception as e:
            print(f"Exception in _get_historical_data: {e}")
            return None
    
    def train_models(self):
        temp_data = self._get_historical_data("temperature")
        pressure_data = self._get_historical_data("pressure")
        
        if temp_data and pressure_data:
            temp_df = preprocess_time_series(temp_data, "value")
            pressure_df = preprocess_time_series(pressure_data, "value")
            
            temp_params = find_best_arima_params(temp_df["value"])
            pressure_params = find_best_arima_params(pressure_df["value"])
            
            if temp_params:
                self.temperature_model = ARIMAModel(p=temp_params[0], d=temp_params[1], q=temp_params[2])
                self.temperature_model.fit(temp_df["value"])
            
            if pressure_params:
                self.pressure_model = ARIMAModel(p=pressure_params[0], d=pressure_params[1], q=pressure_params[2])
                self.pressure_model.fit(pressure_df["value"])
            
            return True
        
        return False
    
    def predict_temperature(self, hours_ahead=1):
        if not self.temperature_model.fitted_model:
            if not self.train_models():
                return None
        
        steps = int(hours_ahead * 60)
        predictions = self.temperature_model.predict(steps=steps)
        
        start_time = datetime.now()
        timestamps = [(start_time + timedelta(minutes=i)).isoformat() for i in range(1, steps + 1)]
        
        prediction_data = [
            {"timestamp": ts, "value": float(val), "exceeds_threshold": float(val) > self.temperature_threshold}
            for ts, val in zip(timestamps, predictions)
        ]
        
        return prediction_data
    
    def predict_pressure(self, hours_ahead=1):
        if not self.pressure_model.fitted_model:
            if not self.train_models():
                return None
        
        steps = int(hours_ahead * 60)
        predictions = self.pressure_model.predict(steps=steps)
        
        start_time = datetime.now()
        timestamps = [(start_time + timedelta(minutes=i)).isoformat() for i in range(1, steps + 1)]
        
        prediction_data = [
            {"timestamp": ts, "value": float(val), "exceeds_threshold": float(val) > self.pressure_threshold}
            for ts, val in zip(timestamps, predictions)
        ]
        
        return prediction_data
    
    def will_exceed_threshold(self, prediction_data):
        if not prediction_data:
            return False
        
        return any(point["exceeds_threshold"] for point in prediction_data)