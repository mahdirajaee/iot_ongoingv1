import os
import logging
import datetime

class ActuatorService:
    def __init__(self, catalog_manager):
        self.catalog_manager = catalog_manager
        self.valve_state = os.getenv("VALVE_DEFAULT_STATE", "closed")
        self.state_change_timestamp = datetime.datetime.now().isoformat()
        logging.info(f"Actuator service initialized with valve state: {self.valve_state}")

    def set_valve_state(self, state):
        if state.lower() not in ["open", "closed"]:
            logging.warning(f"Invalid valve state requested: {state}. Must be 'open' or 'closed'.")
            return False
        
        self.valve_state = state.lower()
        self.state_change_timestamp = datetime.datetime.now().isoformat()
        
        self._update_catalog_status()
        logging.info(f"Valve state set to: {self.valve_state}")
        return True

    def get_valve_state(self):
        return {
            "state": self.valve_state,
            "timestamp": self.state_change_timestamp
        }

    def _update_catalog_status(self):
        status = {
            "valve": {
                "state": self.valve_state,
                "timestamp": self.state_change_timestamp
            }
        }
        self.catalog_manager.update_actuator_status(status)