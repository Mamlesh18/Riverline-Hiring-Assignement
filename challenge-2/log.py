import logging
import os
from datetime import datetime

class Logger:
    def __init__(self):
        try:
            self.logger = logging.getLogger('voice_agent_tester')
            self.logger.setLevel(logging.INFO)
            
            if not self.logger.handlers:
                # Create logs directory if it doesn't exist
                if not os.path.exists('logs'):
                    os.makedirs('logs')
                
                # File handler
                file_handler = logging.FileHandler(
                    f'logs/voice_agent_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
                )
                file_handler.setLevel(logging.INFO)
                
                # Console handler
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                
                # Formatter
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                file_handler.setFormatter(formatter)
                console_handler.setFormatter(formatter)
                
                self.logger.addHandler(file_handler)
                self.logger.addHandler(console_handler)
        except Exception as e:
            print(f"Error initializing logger: {e}")
            raise
    
    def info(self, message):
        try:
            self.logger.info(message)
        except Exception as e:
            print(f"Error logging info message: {e}")
    
    def error(self, message):
        try:
            self.logger.error(message)
        except Exception as e:
            print(f"Error logging error message: {e}")
    
    def warning(self, message):
        try:
            self.logger.warning(message)
        except Exception as e:
            print(f"Error logging warning message: {e}")
    
    def debug(self, message):
        try:
            self.logger.debug(message)
        except Exception as e:
            print(f"Error logging debug message: {e}")

logger = Logger()