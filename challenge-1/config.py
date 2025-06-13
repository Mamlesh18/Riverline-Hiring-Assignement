import os

from dotenv import load_dotenv

load_dotenv()

class DebtCollectionConfig:
    SIP_TRUNK_ID = os.getenv("SIP_TRUNK_ID")
    
    STT_MODEL = "nova-2"
    STT_LANGUAGE = "en"
    STT_SMART_FORMAT = True
    STT_PUNCTUATE = True
    
    LLM_MODEL = "gemini-2.0-flash-exp"
    LLM_TEMPERATURE = 0.5
    
    TTS_MODEL = "aura-asteria-en"
    
    VAD_MIN_SILENCE_DURATION = 0.5
    
    MAX_RETRIES = 2
    RETRY_DELAY = 3
    CONNECTION_TIMEOUT = 10
    INITIAL_SLEEP = 4
    
    DEFAULT_PHONE_NUMBER = "+917358580180"
    DEFAULT_DEBTOR_NAME = "Surya"
    DEFAULT_DEBT_AMOUNT = 5000.0
    DEFAULT_DAYS_OVERDUE = 5
    
    TRANSCRIPT_SAVE_INTERVAL = 30  
    TRANSCRIPT_DIR = "transcripts"
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if not cls.SIP_TRUNK_ID:
            raise ValueError("SIP_TRUNK_ID environment variable is required")
        return True