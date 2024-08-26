from src.game import Game
import logging
import platform
import os
from logging.handlers import RotatingFileHandler

# Determine log file path based on platform
if platform.system() == "Windows":
    log_path = os.path.join(os.getenv("APPDATA"), "bolirana", "bolirana.log")
else:
    log_path = "/var/log/bolirana.log"

# Ensure the log directory exists
log_dir = os.path.dirname(log_path)
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(log_path, maxBytes=1000000, backupCount=3),
        logging.StreamHandler(),
    ],
)


if __name__ == "__main__":
    try:
        game = Game(debug=True)
        game.run()
    except Exception as e:
        logging.error(f": {e}")
