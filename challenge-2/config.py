import os

from dotenv import load_dotenv

from log import logger


class Config:
    def __init__(self):
        try:
            load_dotenv()
            self.api_key = self._get_api_key()
            self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent"
            self.thresholds = {
                'professionalism_score': 85,
                'script_adherence_score': 85,
                'negotiation_effectiveness': 75,
                'objection_handling_score': 75,
                'resolution_success_rate': 65
            }
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Error initializing configuration: {e}")
            raise
    
    def _get_api_key(self):
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                api_key = "GEMINI_API_KEY_PLACEHOLDER"
                logger.warning("Using hardcoded API key - consider setting GEMINI_API_KEY" \
                " environment variable")
            return api_key
        except Exception as e:
            logger.error(f"Error getting API key: {e}")
            raise

config = Config()