class ThresholdUtils:
    def __init__(self, pressure_min, pressure_max, temperature_min, temperature_max):
        self.pressure_min = pressure_min
        self.pressure_max = pressure_max
        self.temperature_min = temperature_min
        self.temperature_max = temperature_max
    
    def is_pressure_critical(self, pressure):
        return pressure < self.pressure_min or pressure > self.pressure_max
    
    def is_temperature_critical(self, temperature):
        return temperature < self.temperature_min or temperature > self.temperature_max
    
    def get_valve_action(self, pressure, temperature):
        if pressure > self.pressure_max or temperature > self.temperature_max:
            return "OPEN"
        elif pressure < self.pressure_min and temperature < self.temperature_min:
            return "CLOSE"
        return None