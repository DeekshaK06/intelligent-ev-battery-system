import time
import random
import logging
from datetime import datetime
from config.settings import TICK_INTERVAL_SEC, CSV_PATH
from src.battery import Battery, BatteryState
from src.data_exporter import DataExporter
from src.fault_injector import FaultInjector

logger = logging.getLogger(__name__)

class SimulatorEngine:
    """Orchestrates runtime iterations, fault injections, and system persistence."""
    
    def __init__(self):
        self.battery = Battery()
        self.exporter = DataExporter(CSV_PATH)
        self.fault_injector = FaultInjector(self.battery)
        self.is_running = False

    def _generate_realistic_current(self) -> float:
        """Simulates real-world patterns instead of white noise (e.g., cruising vs regenerative braking)."""
        # 70% chance driving (discharge), 20% steady state / coasting, 10% regen braking (charge)
        roll = random.random()
        if roll < 0.70:
            return random.uniform(-45.0, -10.0)
        elif roll < 0.90:
            return 0.0
        else:
            return random.uniform(5.0, 25.0)

    def run(self) -> None:
        self.is_running = True
        logger.info("🔋 EV Battery Simulator Engine started.")
        print("\n🚀 Starting Live Telemetry Stream (Press Ctrl+C to stop)...")
        
        tick = 0
        try:
            while self.is_running:
                tick += 1
                
                # Dynamic Fault Injector Scenarios
                if tick == 6:
                    self.fault_injector.trigger_fault("OVERHEATING", duration_ticks=4)
                elif tick == 14:
                    self.fault_injector.trigger_fault("VOLTAGE_ANOMALY", duration_ticks=2)
                elif tick == 22:
                    self.fault_injector.trigger_fault("RAPID_DISCHARGE", duration_ticks=5)

                # Process state machine
                curr_mod, temp_mod = self.fault_injector.process_fault_lifecycle()
                
                if self.fault_injector.active_fault != "RAPID_DISCHARGE":
                    current_input = self._generate_realistic_current() + curr_mod
                    self.battery.update_physics(current_input, external_temp_delta=temp_mod)

                # Bundle Telemetry State
                state = BatteryState(
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    voltage=self.battery.voltage,
                    current=self.battery.current,
                    temperature=self.battery.temperature,
                    soc=round(self.battery.soc, 2),
                    cycle_count=self.battery.cycle_count,
                    status=self.battery.status
                )

                # Export Pipelines
                json_payload = self.exporter.serialize_to_json(state)
                self.exporter.write_to_csv(state)
                
                # Standard Output Display (Mimics modern IoT edge logger)
                print(f"📡 [MQTT-Ready JSON]: {json_payload}")
                
                # Scalability Hook for Future Iteration:
                # self.mqtt_client.publish("vehicles/ev01/battery/telemetry", json_payload)

                time.sleep(TICK_INTERVAL_SEC)
                
        except KeyboardInterrupt:
            logger.info("Simulation interrupted via terminal request.")
            self.stop()
        except Exception as e:
            logger.critical(f"Unhandled Runtime Crash in Engine Loop: {e}", exc_info=True)
            self.stop()

    def stop(self) -> None:
        self.is_running = False
        print("\n🛑 Simulator safely shut down. Log file and CSV data written successfully.")