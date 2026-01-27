import logging
import sys

def setup_logging():
    """
    Sets up a centralized logging configuration.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # helper to silence overly verbose logs from libraries if needed
    # logging.getLogger('werkzeug').setLevel(logging.WARNING) 
