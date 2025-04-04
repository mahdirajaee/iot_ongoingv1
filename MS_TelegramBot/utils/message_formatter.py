def format_temperature_alert(temperature, threshold, timestamp):
    return (
        f"🔥 *TEMPERATURE ALERT* 🔥\n\n"
        f"Measured: *{temperature:.2f}°C*\n"
        f"Threshold: *{threshold:.2f}°C*\n"
        f"Time: {timestamp}\n\n"
        f"This temperature reading exceeds the safe operating threshold."
    )

def format_pressure_alert(pressure, threshold, timestamp):
    return (
        f"⚠️ *PRESSURE ALERT* ⚠️\n\n"
        f"Measured: *{pressure:.2f} PSI*\n"
        f"Threshold: *{threshold:.2f} PSI*\n"
        f"Time: {timestamp}\n\n"
        f"This pressure reading exceeds the safe operating threshold."
    )

def format_prediction_alert(sensor_type, current_value, predicted_value, threshold, time_to_threshold):
    unit = "°C" if sensor_type.lower() == "temperature" else "PSI"
    return (
        f"🔮 *PREDICTION ALERT* 🔮\n\n"
        f"Sensor: *{sensor_type}*\n"
        f"Current value: *{current_value:.2f} {unit}*\n"
        f"Predicted value: *{predicted_value:.2f} {unit}*\n"
        f"Threshold: *{threshold:.2f} {unit}*\n"
        f"Time to threshold: *{time_to_threshold} minutes*\n\n"
        f"Preventive action recommended."
    )

def format_sensor_data(sensor_data):
    temperature = sensor_data.get("temperature", {}).get("value", "N/A")
    temperature_unit = "°C"
    
    pressure = sensor_data.get("pressure", {}).get("value", "N/A")
    pressure_unit = "PSI"
    
    timestamp = sensor_data.get("timestamp", "N/A")
    
    return (
        f"📊 *SENSOR UPDATE* 📊\n\n"
        f"Temperature: *{temperature} {temperature_unit}*\n"
        f"Pressure: *{pressure} {pressure_unit}*\n"
        f"Last update: {timestamp}"
    )

def format_help_message():
    return (
        "🤖 *Available Commands* 🤖\n\n"
        "/start - Start the bot\n"
        "/status - Get current sensor status\n"
        "/valve open - Open the valve\n"
        "/valve close - Close the valve\n"
        "/valve status - Check valve status\n"
        "/help - Show this help message\n"
        "/login username password - Authenticate to access control commands\n"
        "/logout - Log out from the current session"
    )

def format_valve_status(status):
    emoji = "🟢" if status.lower() == "open" else "🔴"
    return f"{emoji} Valve is currently *{status}*"

def format_command_result(command, success):
    if success:
        return f"✅ Command '{command}' executed successfully"
    else:
        return f"❌ Command '{command}' failed to execute"

def format_authentication_result(success, message=None):
    if success:
        return "✅ You are now authenticated. You can use control commands."
    else:
        return f"❌ Authentication failed. {message if message else 'Please try again.'}"