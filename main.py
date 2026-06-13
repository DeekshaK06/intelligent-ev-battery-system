import logging
import sys
import os
from config.settings import LOG_PATH
from src.simulator import SimulatorEngine

def configure_logging():
    """Configures production-grade logging, forcing UTF-8 across all sinks."""
    # Ensure our log file directories exist cleanly
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    
    # 1. Setup a standard FileHandler locked to UTF-8
    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    
    # 2. Setup a StreamHandler locked to standard output using UTF-8 fallback
    stream_output = open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)
    stream_handler = logging.StreamHandler(stream_output)
    
    # Apply standard uniform configuration styling across sinks
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Attach pipelines to the root system logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

if __name__ == "__main__":
    configure_logging()
    engine = SimulatorEngine()
    engine.run()
