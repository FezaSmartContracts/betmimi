import logging
import os
from logging.handlers import RotatingFileHandler

# Logger for the main application
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")

LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)
logging.getLogger("web3.providers.WebSocketProvider").setLevel(logging.WARNING)
logging.getLogger("web3.RequestManager").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=10485760, backupCount=5)
file_handler.setLevel(LOGGING_LEVEL)
file_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))

logging.getLogger("").addHandler(file_handler)
