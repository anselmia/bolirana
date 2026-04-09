import signal
import sys
import logging
import platform
import os
import argparse
from logging.handlers import RotatingFileHandler

from src.game import Game


# Define the signal handler
def signal_handler(sig, frame):
    print("SIGTERM received, exiting gracefully...")
    sys.exit(0)


# Register the signal handler for SIGTERM
signal.signal(signal.SIGTERM, signal_handler)

# Determine log file path based on platform
if platform.system() == "Windows":
    appdata_dir = os.getenv("APPDATA") or os.path.expanduser("~")
    log_path = os.path.join(appdata_dir, "bolirana", "bolirana.log")
else:
    log_path = "/opt/bolirana/log/bolirana.log"
    # Ensure the process is running as the correct user
    geteuid = getattr(os, "geteuid", None)
    seteuid = getattr(os, "seteuid", None)
    getuid = getattr(os, "getuid", None)
    if callable(geteuid) and callable(seteuid) and callable(getuid) and geteuid() == 0:
        seteuid(getuid())  # Switch to the current user (pi)


def parse_args():
    parser = argparse.ArgumentParser(description="Bolirana game launcher")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in windowed debug mode.",
    )
    parser.add_argument(
        "--keyboard",
        "--test-mode",
        dest="keyboard_mode",
        action="store_true",
        help="Disable I2C/ESP32 input and use keyboard-only controls.",
    )
    parser.add_argument(
        "--i2c",
        dest="keyboard_mode",
        action="store_false",
        help="Force hardware I2C input mode.",
    )
    env_keyboard = os.getenv("BOLIRANA_TEST_MODE", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    parser.set_defaults(
        keyboard_mode=platform.system() == "Windows" or env_keyboard,
    )
    return parser.parse_args()
# Ensure the log directory exists
log_dir = os.path.dirname(log_path)
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(log_path, maxBytes=1000000, backupCount=3),
    ],
)

if __name__ == "__main__":
    try:
        args = parse_args()
        run_windowed = args.debug or args.keyboard_mode
        game = Game(debug=run_windowed, keyboard_mode=args.keyboard_mode)
        game.run()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
