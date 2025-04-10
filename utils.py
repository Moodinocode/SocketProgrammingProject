#hashing functiions
#logging functions 
#etc
import logging

logging.basicConfig(
    filename='test.log',
    level=logging.INFO,
    # we can add the threadName in the logging (might be good to show the multithreading)
    format='%(asctime)s - %(levelname)s - %(message)s' # format from stack overflow (https://stackoverflow.com/questions/20240464/python-logging-file-is-not-working-when-using-logging-basicconfig)
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

