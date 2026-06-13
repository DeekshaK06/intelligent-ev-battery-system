import logging
from dataclasses import dataclass
from typing import Optional
from config.settings import (
    VOLTAGE_MIN, VOLTAGE_MAX, TEMP_AMBIENT, 
    BATTERY_CAPACITY_AH, TICK_INTERVAL_SEC
)

logger = logging.getLogger(__name__)

@dataclass
class BatteryState:
    timestamp: str
    battery_id: str
    voltage: float
    current: float
    temperature: float
    soc: float
    soh: float
    cycle_count: int
    battery_state: str
    status: str
    fault_type: Optional[str]

class Battery:
    def __init__(self, battery_id: str, initial_soc: float = 80.0, initial_temp: float = 25.0, initial_cycles: int = 120):
        self._battery_id: str = battery_id
        self._soc: float = max(0.0, min(100.0, initial_soc))
        self._temperature: float = initial_temp
        self._soh: float = 99.8
        self._cycle_count: int = initial_cycles
        self._cumulative_discharge_ah: float = 0.0
        self._voltage: float = self._calculate_voltage()
        self._current: float = 0.0
        self._status: str = "NOMINAL"
        self._fault_type: Optional[str] = None
        self._battery_state: str = "IDLE"

    @property
    def battery_id(self) -> str: return self._battery_id
    @property
    def soc(self) -> float: return self._soc
    @property
    def temperature(self) -> float: return self._temperature
    @property
    def voltage(self) -> float: return self._voltage
    @property
    def current(self) -> float: return self._current
    @property
    def cycle_count(self) -> int: return self._cycle_count
    @property
    def soh(self) -> float: return self._soh
    @property
    def status(self) -> str: return self._status
    @property
    def fault_type(self) -> Optional[str]: return self._fault_type
    @property
    def battery_state(self) -> str: return self._battery_state

    def _calculate_voltage(self) -> float:
        soc_frac = self._soc / 100.0
        ocv = VOLTAGE_MIN + (VOLTAGE_MAX - VOLTAGE_MIN) * (0.4 * soc_frac + 0.6 * (soc_frac ** 3))
        return round(ocv, 2)

    def _evaluate_battery_state(self) -> str:
        if self._status == "FAULT": return "FAULT"
        if self._current > 0.1: return "CHARGING"
        if self._current < -0.1: return "DISCHARGING"
        return "IDLE"

    def update_physics(self, current_draw: float, external_temp_delta: float = 0.0) -> None:
        self._current = current_draw
        hours_passed = TICK_INTERVAL_SEC / 3600.0
        ah_delta = self._current * hours_passed
        
        amplification_factor = 45.0 if self._current != 0 else 1.0
        soc_delta = (ah_delta / BATTERY_CAPACITY_AH) * 100.0 * amplification_factor
        self._soc = max(0.0, min(100.0, self._soc + soc_delta))
        
        if ah_delta < 0:
            self._cumulative_discharge_ah += abs(ah_delta)
            if self._cumulative_discharge_ah >= BATTERY_CAPACITY_AH:
                self._cycle_count += 1
                self._cumulative_discharge_ah -= BATTERY_CAPACITY_AH
                
                base_degradation = 0.005
                degradation_rate_multiplier = 1.0
                if self._temperature > 45.0: degradation_rate_multiplier *= 1.5
                if self._fault_type == "RAPID_DISCHARGE": degradation_rate_multiplier *= 2.0
                if self._cycle_count > 500: degradation_rate_multiplier *= 1.2
                    
                self._soh = max(0.0, round(self._soh - (base_degradation * degradation_rate_multiplier), 3))

        internal_resistance = 0.025 * (2.0 - (self._soh / 100.0))
        self._voltage = round(max(VOLTAGE_MIN - 15.0, min(VOLTAGE_MAX + 15.0, self._calculate_voltage() + (self._current * internal_resistance))), 2)

        joule_heating = (abs(self._current) ** 1.8) * internal_resistance * 0.008
        cooling_to_ambient = 0.015 * (self._temperature - TEMP_AMBIENT)
        self._temperature += joule_heating - cooling_to_ambient + external_temp_delta
        self._temperature = round(max(0.0, self._temperature), 2)

        if self._fault_type is None:
            if self._temperature > 45.0:
                self._status = "FAULT"
                self._fault_type = "OVERHEATING"
            elif self._voltage > VOLTAGE_MAX + 5.0 or self._voltage < VOLTAGE_MIN - 5.0:
                self._status = "FAULT"
                self._fault_type = "VOLTAGE_ANOMALY"
            else:
                self._status = "NOMINAL"
                self._fault_type = None

        self._battery_state = self._evaluate_battery_state()

    def apply_fault_override(self, voltage: float = None, temp: float = None, status: str = "FAULT", fault_type: str = None) -> None:
        if voltage is not None: self._voltage = voltage
        if temp is not None: self._temperature = temp
        self._status = status
        self._fault_type = fault_type
        self._battery_state = self._evaluate_battery_state()
