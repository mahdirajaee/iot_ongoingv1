import cherrypy
import json
import os
from dotenv import load_dotenv
import requests
from services.prediction_service import PredictionService
from services.anomaly_service import AnomalyService

load_dotenv()

class AnalyticsController:
    def __init__(self):
        self.prediction_service = PredictionService()
        self.anomaly_service = AnomalyService()
        self.resource_catalog_url = os.getenv("RESOURCE_CATALOG_URL")
        
        self.predict_temperature = self.PredictTemperature(self)
        self.predict_pressure = self.PredictPressure(self)
        self.temperature_anomalies = self.TemperatureAnomalies(self)
        self.pressure_anomalies = self.PressureAnomalies(self)
        self.cascading_failures = self.CascadingFailures(self)
        self.trigger_valve = self.TriggerValve(self)
        
        self._register_with_catalog()
    
    def _register_with_catalog(self):
        try:
            service_info = {
                "name": os.getenv("SERVICE_NAME"),
                "endpoint": f"http://localhost:{os.getenv('SERVICE_PORT')}",
                "description": "Analytics service for predictive analysis and anomaly detection",
                "endpoints": {
                    "temperature_prediction": "/api/predict/temperature",
                    "pressure_prediction": "/api/predict/pressure",
                    "temperature_anomalies": "/api/anomalies/temperature",
                    "pressure_anomalies": "/api/anomalies/pressure",
                    "cascading_failures": "/api/anomalies/cascading"
                }
            }
            
            response = requests.post(
                f"{self.resource_catalog_url}/api/services",
                json=service_info
            )
            
            if response.status_code != 200:
                print(f"Failed to register with Resource Catalog: {response.text}")
        except Exception as e:
            print(f"Exception during registration: {e}")
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def GET(self):
        return {
            "service": "Analytics Microservice",
            "status": "running",
            "endpoints": [
                "/api/predict/temperature",
                "/api/predict/pressure",
                "/api/anomalies/temperature",
                "/api/anomalies/pressure",
                "/api/anomalies/cascading",
                "/api/trigger-valve"
            ]
        }
    
    @cherrypy.expose
    class PredictTemperature:
        def __init__(self, parent):
            self.parent = parent
        
        @cherrypy.tools.json_out()
        def GET(self, hours=1):
            try:
                hours = float(hours)
                predictions = self.parent.prediction_service.predict_temperature(hours_ahead=hours)
                
                if not predictions:
                    raise cherrypy.HTTPError(500, "Failed to generate temperature predictions")
                
                threshold_exceeded = self.parent.prediction_service.will_exceed_threshold(predictions)
                
                if threshold_exceeded:
                    self.parent.anomaly_service.send_alert(
                        "temperature_prediction",
                        f"Temperature predicted to exceed threshold in the next {hours} hours",
                        predictions
                    )
                
                return {
                    "predictions": predictions,
                    "threshold_exceeded": threshold_exceeded,
                    "hours_ahead": hours
                }
                
            except Exception as e:
                raise cherrypy.HTTPError(500, f"Error in temperature prediction: {str(e)}")
    
    @cherrypy.expose
    class PredictPressure:
        def __init__(self, parent):
            self.parent = parent
            
        @cherrypy.tools.json_out()
        def GET(self, hours=1):
            try:
                hours = float(hours)
                predictions = self.parent.prediction_service.predict_pressure(hours_ahead=hours)
                
                if not predictions:
                    raise cherrypy.HTTPError(500, "Failed to generate pressure predictions")
                
                threshold_exceeded = self.parent.prediction_service.will_exceed_threshold(predictions)
                
                if threshold_exceeded:
                    self.parent.anomaly_service.send_alert(
                        "pressure_prediction",
                        f"Pressure predicted to exceed threshold in the next {hours} hours",
                        predictions
                    )
                
                return {
                    "predictions": predictions,
                    "threshold_exceeded": threshold_exceeded,
                    "hours_ahead": hours
                }
                
            except Exception as e:
                raise cherrypy.HTTPError(500, f"Error in pressure prediction: {str(e)}")
    
    @cherrypy.expose
    class TemperatureAnomalies:
        def __init__(self, parent):
            self.parent = parent
            
        @cherrypy.tools.json_out()
        def GET(self):
            try:
                anomalies = self.parent.anomaly_service.detect_anomalies("temperature")
                
                critical_anomalies = [a for a in anomalies if a["is_critical"]]
                if critical_anomalies:
                    self.parent.anomaly_service.send_alert(
                        "temperature_anomaly",
                        f"Critical temperature anomalies detected",
                        critical_anomalies
                    )
                
                return {
                    "anomalies": anomalies,
                    "count": len(anomalies),
                    "critical_count": len(critical_anomalies)
                }
                
            except Exception as e:
                raise cherrypy.HTTPError(500, f"Error detecting temperature anomalies: {str(e)}")
    
    @cherrypy.expose
    class PressureAnomalies:
        def __init__(self, parent):
            self.parent = parent
            
        @cherrypy.tools.json_out()
        def GET(self):
            try:
                anomalies = self.parent.anomaly_service.detect_anomalies("pressure")
                
                critical_anomalies = [a for a in anomalies if a["is_critical"]]
                if critical_anomalies:
                    self.parent.anomaly_service.send_alert(
                        "pressure_anomaly",
                        f"Critical pressure anomalies detected",
                        critical_anomalies
                    )
                
                return {
                    "anomalies": anomalies,
                    "count": len(anomalies),
                    "critical_count": len(critical_anomalies)
                }
                
            except Exception as e:
                raise cherrypy.HTTPError(500, f"Error detecting pressure anomalies: {str(e)}")
    
    @cherrypy.expose
    class CascadingFailures:
        def __init__(self, parent):
            self.parent = parent
            
        @cherrypy.tools.json_out()
        def GET(self):
            try:
                risk_detected = self.parent.anomaly_service.detect_cascading_failures()
                
                if risk_detected:
                    self.parent.anomaly_service.send_alert(
                        "cascading_failure",
                        "Risk of cascading failure detected. Immediate attention required.",
                        {"risk_level": "high"}
                    )
                    
                    self.parent.trigger_valve(action="close", automatic=True)
                
                return {
                    "cascading_failure_risk": risk_detected,
                    "automatic_action_taken": risk_detected
                }
                
            except Exception as e:
                raise cherrypy.HTTPError(500, f"Error detecting cascading failures: {str(e)}")
    
    @cherrypy.expose
    class TriggerValve:
        def __init__(self, parent):
            self.parent = parent
            
        @cherrypy.tools.json_out()
        @cherrypy.tools.json_in()
        def POST(self):
            try:
                if hasattr(cherrypy.request, 'json'):
                    data = cherrypy.request.json
                    action = data.get("action", "close")
                else:
                    action = "close"
                
                automatic = False
                if hasattr(cherrypy.request, 'json'):
                    automatic = data.get("automatic", False)
                
                if action not in ["open", "close"]:
                    raise cherrypy.HTTPError(400, "Invalid action. Must be 'open' or 'close'.")
                
                try:
                    response = requests.get(f"{self.parent.resource_catalog_url}/api/services/control_center")
                    if response.status_code == 200:
                        control_center_info = response.json()
                        control_center_url = control_center_info.get("endpoint")
                        
                        if not control_center_url:
                            raise Exception("Control Center URL not found in catalog")
                        
                        valve_response = requests.post(
                            f"{control_center_url}/api/valve",
                            json={
                                "action": action,
                                "reason": "Anomaly or prediction threshold exceeded",
                                "automatic": automatic
                            }
                        )
                        
                        if valve_response.status_code != 200:
                            raise Exception(f"Failed to trigger valve: {valve_response.text}")
                        
                        return {
                            "success": True,
                            "action": action,
                            "automatic": automatic,
                            "message": f"Valve {action} command sent successfully"
                        }
                    else:
                        raise Exception(f"Failed to get Control Center info: {response.text}")
                except Exception as e:
                    raise cherrypy.HTTPError(500, f"Error communicating with Control Center: {str(e)}")
                    
            except Exception as e:
                raise cherrypy.HTTPError(500, f"Error triggering valve: {str(e)}")
                
        @cherrypy.tools.json_out()
        def GET(self, action="close", automatic=False):
            try:
                if action not in ["open", "close"]:
                    raise cherrypy.HTTPError(400, "Invalid action. Must be 'open' or 'close'.")
                
                automatic = str(automatic).lower() in ['true', '1', 't', 'y', 'yes']
                
                try:
                    response = requests.get(f"{self.parent.resource_catalog_url}/api/services/control_center")
                    if response.status_code == 200:
                        control_center_info = response.json()
                        control_center_url = control_center_info.get("endpoint")
                        
                        if not control_center_url:
                            raise Exception("Control Center URL not found in catalog")
                        
                        valve_response = requests.post(
                            f"{control_center_url}/api/valve",
                            json={
                                "action": action,
                                "reason": "Anomaly or prediction threshold exceeded",
                                "automatic": automatic
                            }
                        )
                        
                        if valve_response.status_code != 200:
                            raise Exception(f"Failed to trigger valve: {valve_response.text}")
                        
                        return {
                            "success": True,
                            "action": action,
                            "automatic": automatic,
                            "message": f"Valve {action} command sent successfully"
                        }
                    else:
                        raise Exception(f"Failed to get Control Center info: {response.text}")
                except Exception as e:
                    raise cherrypy.HTTPError(500, f"Error communicating with Control Center: {str(e)}")
                    
            except Exception as e:
                raise cherrypy.HTTPError(500, f"Error triggering valve: {str(e)}")

def get_app():
    controller = AnalyticsController()
    
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')],
        }
    }
    
    app = cherrypy.tree.mount(controller, '/', conf)
    return app