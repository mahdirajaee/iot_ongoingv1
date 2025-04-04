import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller

def preprocess_time_series(data, column_name):
    df = pd.DataFrame(data)
    
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
    
    df[column_name].interpolate(method='time', inplace=True)
    
    df = df.resample('1min').mean()
    
    return df

def check_stationarity(time_series):
    result = adfuller(time_series.dropna())
    is_stationary = result[1] <= 0.05
    return is_stationary

def make_stationary(time_series):
    if check_stationarity(time_series):
        return time_series, 0
    
    d = 0
    diff_series = time_series.copy()
    
    while d < 2:
        diff_series = diff_series.diff().dropna()
        d += 1
        if check_stationarity(diff_series):
            break
    
    return diff_series, d

def inverse_transform(predictions, original_series, d):
    if d == 0:
        return predictions
    
    last_value = original_series.iloc[-1]
    undiff_predictions = [last_value]
    
    for pred in predictions:
        undiff_predictions.append(undiff_predictions[-1] + pred)
    
    return undiff_predictions[1:]