import random
import logging
from typing import Optional
from src.battery import Battery

logger = logging.getLogger(__name__)

class FaultInjector:
    def __init__(self, battery: Battery):
        self.battery: Battery = battery
        self.active_fault: Optional[str] = None
        self._fault_duration_ticks: int = 0

    def trigger_fault(self, fault_type: str, duration_ticks: int = 5) -> None:
        self.active_fault = fault_type
        self._fault_duration_ticks = duration_ticks
        self.battery.apply_fault_override(status="FAULT", fault_type=fault_type)
        logger.warning(f"?? Explicit fault injected: [{fault_type}] for {duration_ticks} execution cycles.")

    def process_fault_lifecycle(self) -> tuple[float, float]:
        if not self.active_fault or self._fault_duration_ticks <= 0:
            if self.active_fault:
                self.battery.apply_fault_override(status="NOMINAL", fault_type=None)
                self.active_fault = None
            return 0.0, 0.0

        self._fault_duration_ticks -= 1
        
        if self.active_fault == "OVERHEATING":
            return 0.0, random.uniform(5.0, 8.0)
        elif self.active_fault == "RAPID_DISCHARGE":
            self.battery.update_physics(current_draw=-120.0, external_temp_delta=2.0)
            self.battery.apply_fault_override(status="FAULT", fault_type="RAPID_DISCHARGE")
            return 0.0, 0.0
        elif self.active_fault == "VOLTAGE_ANOMALY":
            self.battery.apply_fault_override(voltage=random.uniform(310.0, 330.0), status="FAULT", fault_type="VOLTAGE_ANOMALY")
            return 0.0, 0.0

        return 0.0, 0.0
