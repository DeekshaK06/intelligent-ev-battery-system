import random
import logging
from typing import Optional, Dict
from src.battery import Battery

logger = logging.getLogger(__name__)

class FaultInjector:
    def __init__(self, batteries: Dict[str, Battery]):
        self.batteries: Dict[str, Battery] = batteries
        self.active_faults: Dict[str, Optional[str]] = {b_id: None for b_id in batteries}
        self._fault_durations: Dict[str, int] = {b_id: 0 for b_id in batteries}

    def trigger_fault(self, battery_id: str, fault_type: str, duration_ticks: int = 5) -> None:
        if battery_id in self.batteries:
            self.active_faults[battery_id] = fault_type
            self._fault_durations[battery_id] = duration_ticks
            self.batteries[battery_id].apply_fault_override(status="FAULT", fault_type=fault_type)
            logger.warning(f"?? Target Injected: [{fault_type}] loaded on asset {battery_id} for {duration_ticks} cycles.")

    def process_fault_lifecycle(self, battery_id: str) -> tuple[float, float]:
        target_battery = self.batteries.get(battery_id)
        if not target_battery: return 0.0, 0.0

        active_fault = self.active_faults[battery_id]
        duration = self._fault_durations[battery_id]

        if not active_fault or duration <= 0:
            if active_fault:
                target_battery.apply_fault_override(status="NOMINAL", fault_type=None)
                self.active_faults[battery_id] = None
            return 0.0, 0.0

        self._fault_durations[battery_id] -= 1
        
        if active_fault == "OVERHEATING": return 0.0, random.uniform(5.0, 8.0)
        elif active_fault == "RAPID_DISCHARGE":
            target_battery.update_physics(current_draw=-135.0, external_temp_delta=2.5)
            target_battery.apply_fault_override(status="FAULT", fault_type="RAPID_DISCHARGE")
            return 0.0, 0.0
        elif active_fault == "VOLTAGE_ANOMALY":
            target_battery.apply_fault_override(voltage=random.uniform(310.0, 325.0), status="FAULT", fault_type="VOLTAGE_ANOMALY")
            return 0.0, 0.0
        return 0.0, 0.0
