import logging
import sys
from app.core import get_log_level

def setup_logging():
    logging.basicConfig(
        level=get_log_level(),
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    ) 