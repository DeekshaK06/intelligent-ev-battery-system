import random
import logging
from src.battery import Battery

logger = logging.getLogger(__name__)

class FaultInjector:
    """Simulates operational anomalies and harsh environment events."""
    
    def __init__(self, battery: Battery):
        self.battery = battery
        self.active_fault = None
        self._fault_duration_ticks = 0

    def trigger_fault(self, fault_type: str, duration_ticks: int = 5) -> None:
        self.active_fault = fault_type
        self._fault_duration_ticks = duration_ticks
        logger.warning(f"⚠️ Fault injected: [{fault_type}] for {duration_ticks} ticks.")

    def process_fault_lifecycle(self) -> float:
        """
        Processes active faults and returns modifiers.
        Returns: tuple of (current_modifier, temp_modifier)
        """
        if not self.active_fault or self._fault_duration_ticks <= 0:
            self.active_fault = None
            return 0.0, 0.0

        self._fault_duration_ticks -= 1
        
        if self.active_fault == "OVERHEATING":
            # Rapid thermal runway modifier
            return 0.0, random.uniform(4.0, 7.0)
            
        elif self.active_fault == "RAPID_DISCHARGE":
            # Massive structural current draw overriding standard driving profiles
            self.battery.update_physics(current_draw=-120.0, external_temp_delta=1.5)
            return 0.0, 0.0
            
        elif self.active_fault == "VOLTAGE_ANOMALY":
            # Simulates transient sensor or cell degradation drop
            self.battery.apply_fault_override(voltage=random.uniform(310.0, 335.0), status="FAULT_CRITICAL")
            return 0.0, 0.0

        return 0.0, 0.0