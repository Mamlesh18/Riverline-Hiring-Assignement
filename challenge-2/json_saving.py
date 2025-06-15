import json
import os
from datetime import datetime
from typing import Any, Dict

from log import logger


class JSONSaver:
    def __init__(self):
        try:
            self.results_dir = 'results'
            if not os.path.exists(self.results_dir):
                os.makedirs(self.results_dir)
            logger.info("JSONSaver initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing JSONSaver: {e}")
            raise
    
    def save_results(self, results: Dict[str, Any], filename: str = None) -> str:
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"voice_agent_test_results_{timestamp}.json"
            
            filepath = os.path.join(self.results_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Results saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving results to JSON: {e}")
            try:
                with open('voice_agent_test_results.json', 'w') as f:
                    json.dump(results, f, indent=2)
                logger.info("Results saved to fallback location: voice_agent_test_results.json")
                return 'voice_agent_test_results.json'
            except Exception as fallback_error:
                logger.error(f"Error with fallback save: {fallback_error}")
                raise
    
    def load_results(self, filepath: str) -> Dict[str, Any]:
        try:
            with open(filepath, 'r') as f:
                results = json.load(f)
            logger.info(f"Results loaded from: {filepath}")
            return results
        except Exception as e:
            logger.error(f"Error loading results from JSON: {e}")
            raise

json_saver = JSONSaver()