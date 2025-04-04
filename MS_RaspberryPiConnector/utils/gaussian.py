import numpy as np

def generate_gaussian_value(mean, std_dev, min_val=None, max_val=None):
    value = np.random.normal(mean, std_dev)
    
    if min_val is not None and value < min_val:
        value = min_val
    
    if max_val is not None and value > max_val:
        value = max_val
    
    return round(value, 2)