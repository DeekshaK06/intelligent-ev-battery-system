import logging
from dataclasses import dataclass, asdict
from config.settings import (
    VOLTAGE_MIN, VOLTAGE_MAX, TEMP_AMBIENT, 
    BATTERY_CAPACITY_AH, TICK_INTERVAL_SEC
)

logger = logging.getLogger(__name__)

@dataclass
class BatteryState:
    timestamp: str
    voltage: float
    current: float
    temperature: float
    soc: float
    cycle_count: float
    status: str

class Battery:
    def __init__(self, initial_soc: float = 80.0, initial_temp: float = 25.0):
        self._soc = max(0.0, min(100.0, initial_soc))
        self._temperature = initial_temp
        self._cycle_count = 120.0
        self._voltage = self._calculate_voltage()
        self._current = 0.0
        self._status = "NOMINAL"

    @property
    def soc(self) -> float: return self._soc
    @property
    def temperature(self) -> float: return self._temperature
    @property
    def voltage(self) -> float: return self._voltage
    @property
    def current(self) -> float: return self._current
    @property
    def cycle_count(self) -> float: return self._cycle_count
    @property
    def status(self) -> str: return self._status

    def _calculate_voltage(self) -> float:
        soc_frac = self._soc / 100.0
        ocv = VOLTAGE_MIN + (VOLTAGE_MAX - VOLTAGE_MIN) * (0.5 * soc_frac + 0.5 * (soc_frac ** 3))
        return round(ocv, 2)

    def update_physics(self, current_draw: float, external_temp_delta: float = 0.0) -> None:
        self._current = current_draw
        hours_passed = TICK_INTERVAL_SEC / 3600.0
        ah_delta = self._current * hours_passed
        
        self._soc = max(0.0, min(100.0, self._soc + (ah_delta / BATTERY_CAPACITY_AH) * 100.0))
        
        if ah_delta < 0:
            self._cycle_count += abs(ah_delta) / BATTERY_CAPACITY_AH

        internal_resistance = 0.02
        self._voltage = round(max(VOLTAGE_MIN - 10.0, min(VOLTAGE_MAX + 10.0, self._calculate_voltage() + (self._current * internal_resistance))), 2)

        joule_heating = (self._current ** 2) * internal_resistance * 0.005
        cooling_to_ambient = 0.02 * (self._temperature - TEMP_AMBIENT)
        self._temperature += joule_heating - cooling_to_ambient + external_temp_delta
        self._temperature = round(max(0.0, self._temperature), 2)

        if self._temperature > 45.0 or self._voltage > VOLTAGE_MAX + 5 or self._voltage < VOLTAGE_MIN - 5:
            self._status = "FAULT"
        else:
            self._status = "NOMINAL"

    def apply_fault_override(self, voltage: float = None, temp: float = None, status: str = "FAULT") -> None:
        if voltage is not None: self._voltage = voltage
        if temp is not None: self._temperature = temp
        self._status = status
