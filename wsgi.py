from app import app
from waitress import serve
from src.logging_config import setup_logging
import logging

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger("wsgi")
    
    import webbrowser
    from threading import Timer
    
    def open_browser():
        webbrowser.open_new("http://localhost:8080")
        
    Timer(1.5, open_browser).start()
    
    logger.info("Starting production server on http://0.0.0.0:8080")
    serve(app, host='0.0.0.0', port=8080)
