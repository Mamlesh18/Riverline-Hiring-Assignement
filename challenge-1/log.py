import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debt_collection_agent.log'),
        logging.StreamHandler()
    ]
)

# Get the actual logger
logger = logging.getLogger("debt_collection_agent")
