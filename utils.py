#hashing functiions
#logging functions 
#etc
import logging

logging.basicConfig(
    filename='test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log(level, message):
    try:
        if level == "debug":
            logging.debug(message)
        elif level == "info":
            logging.info(message)
        elif level == "warning":
            logging.warning(message)
        elif level == "error":
            logging.error(message)
        elif level == "critical":
            logging.critical(message)
    except Exception as e:
        print(f"Logging error: {str(e)}")  # Fallback to print if logging fails

