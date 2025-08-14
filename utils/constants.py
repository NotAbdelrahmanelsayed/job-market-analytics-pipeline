from utils.logging_config import setup_logging
from pathlib import Path
import configparser
import datetime


# Prepare the logger
logger = setup_logging()

# Getting the config parser
config = configparser.ConfigParser()
conf_path = Path(__file__).resolve().parents[1] / "config/configuration.conf"
