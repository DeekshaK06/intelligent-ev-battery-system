import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional
from config.settings import TICK_INTERVAL_SEC, CSV_PATH
from src.battery import Battery, BatteryState
from src.data_exporter import DataExporter
from src.fault_injector import FaultInjector

logger = logging.getLogger(__name__)

class SimulatorEngine:
    def __init__(self):
        self.battery_ids: List[str] = ["EV001", "EV002", "EV003", "EV004", "EV005"]
        self.batteries: Dict[str, Battery] = {
            b_id: Battery(battery_id=b_id, initial_soc=random.uniform(70.0, 85.0), initial_cycles=random.randint(110, 150))
            for b_id in self.battery_ids
        }
        self.exporter: DataExporter = DataExporter(CSV_PATH)
        self.fault_injector: FaultInjector = FaultInjector(self.batteries)
        self.is_running: bool = False

    def _generate_realistic_current(self, battery_id: str) -> float:
        roll = random.random()
        if roll < 0.55: return random.uniform(-50.0, -15.0)
        elif roll < 0.75: return 0.0
        else: return random.uniform(12.0, 40.0)

    def run(self) -> None:
        self.is_running = True
        logger.info(f"Fleet Management Parallel Digital Twin initialized")
        print("\n🚀 Fleet Engine Operational. Processing Parallel Twin Vectors...")
        
        tick = 0
        try:
            while self.is_running:
                tick += 1
                timestamp_str = datetime.utcnow().isoformat() + "Z"
                
                if tick == 4:
                    self.fault_injector.trigger_fault("EV002", "OVERHEATING", duration_ticks=3)

                for b_id in self.battery_ids:
                    battery = self.batteries[b_id]
                    curr_mod, temp_mod = self.fault_injector.process_fault_lifecycle(b_id)
                    
                    current_input = self._generate_realistic_current(b_id) + curr_mod
                    battery.update_physics(current_input, external_temp_delta=temp_mod)

                    state = BatteryState(
                        timestamp=timestamp_str,
                        battery_id=battery.battery_id,
                        voltage=battery.voltage,
                        current=battery.current,
                        temperature=battery.temperature,
                        soc=round(battery.soc, 1),
                        soh=round(battery.soh, 2),
                        cycle_count=int(battery.cycle_count),
                        battery_state=battery.battery_state,
                        status=battery.status,
                        fault_type=battery.fault_type
                    )

                    json_payload = self.exporter.serialize_to_json(state)
                    self.exporter.write_to_csv(state)
                    
                    if state.battery_state == "FAULT": state_emoji = "⚠️"
                    elif state.battery_state == "CHARGING": state_emoji = "⚡"
                    elif state.battery_state == "DISCHARGING": state_emoji = "🔋"
                    else: state_emoji = "🅿️"

                    print(f"📡 [STREAM -> {b_id}] {state_emoji}: {json_payload}")
                
                print(f"--- [TIMESTEP CYCLE {tick} COMPLETELY LOGGED] ---\n")
                time.sleep(TICK_INTERVAL_SEC)
                
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            self.stop()

    def stop(self) -> None:
        self.is_running = False
        print("\n🛑 Fleet platform safely shut down.")
