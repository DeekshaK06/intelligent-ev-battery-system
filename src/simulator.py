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
    """Manages iterative evaluation loops, system physics steps, and operational tasks."""
    
    def __init__(self):
        self.battery: Battery = Battery(battery_id="EV001", initial_soc=80.0)
        self.exporter: DataExporter = DataExporter(CSV_PATH)
        self.fault_injector: FaultInjector = FaultInjector(self.battery)
        self.is_running: bool = False

    def _generate_realistic_current(self) -> float:
        """Evaluates driving current loads, alternating between charge and discharge modes."""
        roll = random.random()
        if roll < 0.50:
            return random.uniform(-45.0, -15.0)  # Standard Discharge profile load
        elif roll < 0.75:
            return 0.0                           # Stationary equilibrium state
        else:
            return random.uniform(10.0, 35.0)    # Active regenerative charging load

    def run(self) -> None:
        """Starts the main runtime engine thread loop."""
        self.is_running = True
        logger.info(f"🔋 Digital Twin platform tracking initialized for {self.battery.battery_id}.")
        print("\n🚀 Starting Upgraded Real-Time Stream...")
        
        tick = 0
        try:
            while self.is_running:
                tick += 1
                
                # Execution schedule for fault injection scenarios
                if tick == 5:
                    self.fault_injector.trigger_fault("OVERHEATING", duration_ticks=3)
                elif tick == 12:
                    self.fault_injector.trigger_fault("VOLTAGE_ANOMALY", duration_ticks=2)
                elif tick == 18:
                    self.fault_injector.trigger_fault("RAPID_DISCHARGE", duration_ticks=4)

                # Step execution physics matrices
                curr_mod, temp_mod = self.fault_injector.process_fault_lifecycle()
                
                if self.fault_injector.active_fault != "RAPID_DISCHARGE":
                    current_input = self._generate_realistic_current() + curr_mod
                    self.battery.update_physics(current_input, external_temp_delta=temp_mod)

                # Gather and export expanded structural states (ALL REQUIRED ARGUMENTS PASSED HERE)
                state = BatteryState(
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    battery_id=self.battery.battery_id,
                    voltage=self.battery.voltage,
                    current=self.battery.current,
                    temperature=self.battery.temperature,
                    soc=round(self.battery.soc, 1),
                    soh=round(self.battery.soh, 1),
                    cycle_count=int(self.battery.cycle_count),
                    status=self.battery.status,
                    fault_type=self.battery.fault_type
                )

                json_payload = self.exporter.serialize_to_json(state)
                self.exporter.write_to_csv(state)
                
                print(f"📡 [DATA STREAM]: {json_payload}")
                time.sleep(TICK_INTERVAL_SEC)
                
        except KeyboardInterrupt:
            logger.info("Simulation loop paused via user terminal exit signature.")
            self.stop()
        except Exception as e:
            logger.critical(f"Unhandled critical execution error in simulation runtime: {e}", exc_info=True)
            self.stop()

    def stop(self) -> None:
        self.is_running = False
        print("\n🛑 Simulator safely shut down. Log file and CSV data written successfully.")