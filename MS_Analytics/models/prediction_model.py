import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pickle
import os

class ARIMAModel:
    def __init__(self, p=1, d=1, q=1, seasonal_order=(0, 0, 0, 0)):
        self.p = p
        self.d = d
        self.q = q
        self.seasonal_order = seasonal_order
        self.model = None
        self.fitted_model = None
    
    def fit(self, time_series):
        try:
            self.model = SARIMAX(
                time_series, 
                order=(self.p, self.d, self.q),
                seasonal_order=self.seasonal_order,
                enforce_stationarity=False
            )
            self.fitted_model = self.model.fit(disp=False)
            return True
        except Exception as e:
            print(f"Error fitting ARIMA model: {e}")
            return False
    
    def predict(self, steps=10):
        if self.fitted_model is None:
            return None
        
        forecast = self.fitted_model.forecast(steps=steps)
        return forecast
    
    def save_model(self, filepath):
        if self.fitted_model is not None:
            with open(filepath, 'wb') as f:
                pickle.dump(self.fitted_model, f)
            return True
        return False
    
    def load_model(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                self.fitted_model = pickle.load(f)
            return True
        return False

def find_best_arima_params(time_series, p_range=(0, 2), d_range=(0, 2), q_range=(0, 2)):
    best_aic = float("inf")
    best_params = None
    
    for p in range(p_range[0], p_range[1] + 1):
        for d in range(d_range[0], d_range[1] + 1):
            for q in range(q_range[0], q_range[1] + 1):
                try:
                    model = ARIMA(time_series, order=(p, d, q))
                    model_fit = model.fit()
                    aic = model_fit.aic
                    
                    if aic < best_aic:
                        best_aic = aic
                        best_params = (p, d, q)
                except:
                    continue
    
    return best_params