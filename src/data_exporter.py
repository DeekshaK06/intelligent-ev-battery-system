import csv
import json
import os
import logging
from dataclasses import asdict
from src.battery import BatteryState

logger = logging.getLogger(__name__)

class DataExporter:
    """Handles serialization and thread-safe persistence pipelines."""
    
    def __init__(self, csv_filepath: str):
        self.csv_filepath = csv_filepath
        self._initialize_csv()

    def _initialize_csv(self) -> None:
        """Write headers if file does not exist."""
        if not os.path.exists(self.csv_filepath):
            try:
                with open(self.csv_filepath, mode='w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Voltage_V", "Current_A", "Temperature_C", "SOC_Pct", "CycleCount", "Status"])
                logger.info(f"Initialized CSV storage telemetry at {self.csv_filepath}")
            except IOError as e:
                logger.error(f"Failed to initialize CSV file: {e}")
                raise

    def serialize_to_json(self, state: BatteryState) -> str:
        """Converts state into a structured JSON string for streaming/MQTT transport."""
        try:
            return json.dumps(asdict(state))
        except TypeError as e:
            logger.error(f"JSON Serialization failed: {e}")
            return "{}"

    def write_to_csv(self, state: BatteryState) -> None:
        """Appends metrics row safely to system disk storage."""
        try:
            with open(self.csv_filepath, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    state.timestamp, state.voltage, state.current, 
                    state.temperature, state.soc, round(state.cycle_count, 4), state.status
                ])
        except IOError as e:
            logger.error(f"Failed writing telemetry row to CSV: {e}")
