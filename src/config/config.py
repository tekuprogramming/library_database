import configparser
import logging
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(os.path.dirname(BASE_DIR), "config.ini")

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

logging.basicConfig(
    level=getattr(logging, config.get("app", "log_level", fallback="INFO")),
    format="%(asctime)s - %(levelname)s - %(message)s",
)