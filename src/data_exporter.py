import csv
import json
import os
import logging
from dataclasses import asdict
from src.battery import BatteryState

logger = logging.getLogger(__name__)

class DataExporter:
    def __init__(self, csv_filepath: str):
        self.csv_filepath: str = csv_filepath
        self._initialize_csv()

    def _initialize_csv(self) -> None:
        if not os.path.exists(self.csv_filepath):
            try:
                with open(self.csv_filepath, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "timestamp", "battery_id", "voltage", "current", 
                        "temperature", "soc", "soh", "cycle_count", "status", "fault_type"
                    ])
            except IOError as e:
                logger.error(f"Failed to generate telemetry CSV matrix layout: {e}")
                raise

    def serialize_to_json(self, state: BatteryState) -> str:
        try:
            return json.dumps(asdict(state))
        except TypeError as e:
            logger.error(f"Structured JSON output serialization failed: {e}")
            return "{}"

    def write_to_csv(self, state: BatteryState) -> None:
        try:
            with open(self.csv_filepath, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    state.timestamp, state.battery_id, state.voltage, state.current, 
                    state.temperature, state.soc, state.soh, state.cycle_count, 
                    state.status, state.fault_type if state.fault_type else ""
                ])
        except IOError as e:
            logger.error(f"Failed logging array payload mapping directly to CSV: {e}")
