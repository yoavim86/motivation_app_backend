import logging
import sys
from app.config import Config

def setup_logging():
    logging.basicConfig(
        level=Config.LOG_LEVEL,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    ) 