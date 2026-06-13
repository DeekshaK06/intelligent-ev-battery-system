import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# File Paths
CSV_PATH = os.path.join(DATA_DIR, "telemetry.csv")
LOG_PATH = os.path.join(LOG_DIR, "simulator.log")

# Battery Limits
VOLTAGE_MIN = 350.0
VOLTAGE_MAX = 420.0
CURRENT_MAX_DISCHARGE = -50.0  # Amperes (Negative = Discharging)
CURRENT_MAX_CHARGE = 40.0     # Amperes (Positive = Charging)
TEMP_AMBIENT = 25.0            # Celsius
TEMP_MAX_SAFE = 45.0          # Celsius
BATTERY_CAPACITY_AH = 100.0    # Ampere-hours for realistic SOC math

# Simulation Settings
TICK_INTERVAL_SEC = 5