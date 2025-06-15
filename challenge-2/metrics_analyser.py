import requests
import json
import time
from typing import List, Dict, Any
from config import config
from log import logger

class GeminiAPI:
    def __init__(self, api_key: str):
        try:
            self.api_key = api_key
            self.base_url = config.base_url
            logger.info("GeminiAPI initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing GeminiAPI: {e}")
            raise
    
    def generate_response(self, prompt: str) -> str:
        try:
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            response_text = result['candidates'][0]['content']['parts'][0]['text']
            return response_text
        except Exception as e:
            logger.error(f"API Error: {e}")
            return "Sorry, I'm having technical difficulties."

class MetricsAnalyzer:
    def __init__(self, api_key: str):
        try:
            self.gemini = GeminiAPI(api_key)
            self.thresholds = config.thresholds
            logger.info("MetricsAnalyzer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing MetricsAnalyzer: {e}")
            raise
    
    def create_metrics_prompt(self, conversation_history: List[str], persona_info: Dict[str, Any]) -> str:
        try:
            conversation_text = '\n'.join(conversation_history)
            
            prompt = """
Analyze this debt collection conversation and provide metrics in JSON format.
CONVERSATION:
{}
CUSTOMER PERSONA: {} - {}
Analyze and rate each metric from 0-100:
1. PROFESSIONALISM_SCORE: How polite, respectful, and professional was the agent?
2. SCRIPT_ADHERENCE_SCORE: Did agent follow proper opening, mention bank name, overdue amount?
3. NEGOTIATION_EFFECTIVENESS: Did agent offer extensions/alternatives when customer couldn't pay?
4. OBJECTION_HANDLING_SCORE: How well did agent handle customer objections with empathy?
5. RESOLUTION_SUCCESS_RATE: Did conversation end with clear next steps or resolution?
6. REPETITION_ISSUES: Did agent repeat same phrases excessively? (0=no repetition, 100=highly repetitive)
7. RELEVANCE_SCORE: Did agent stay on topic? (0=irrelevant, 100=highly relevant)
8. CONVERSATION_LENGTH: Number of total exchanges
9. CUSTOMER_SATISFACTION: Based on customer responses, how satisfied did they seem? (0-100)
10. COMPLIANCE_SCORE: Did agent avoid aggressive language, threats, or inappropriate tactics?
RETURN ONLY JSON in this exact format:
{{
    "professionalism_score": 85,
    "script_adherence_score": 90,
    "negotiation_effectiveness": 75,
    "objection_handling_score": 80,
    "resolution_success_rate": 70,
    "repetition_issues": 15,
    "relevance_score": 95,
    "conversation_length": 8,
    "customer_satisfaction": 75,
    "compliance_score": 90,
    "overall_performance": 82,
    "meets_thresholds": true,
    "areas_for_improvement": ["negotiation skills", "resolution tactics"],
    "strengths": ["professional tone", "script adherence"]
}}
""".format(conversation_text, persona_info['personality'], persona_info['scenario'])
            
            logger.info("Metrics prompt created successfully")
            return prompt
        except Exception as e:
            logger.error(f"Error creating metrics prompt: {e}")
            return ""
    
    def analyze_conversation(self, conversation_history: List[str], persona_info: Dict[str, Any]) -> Dict[str, Any]:
        try:
            time.sleep(1)
            
            prompt = self.create_metrics_prompt(conversation_history, persona_info)
            response = self.gemini.generate_response(prompt)
            
            
            json_str = ""
            
            if "```json" in response:
                start_marker = response.find("```json") + 7
                end_marker = response.find("```", start_marker)
                json_str = response[start_marker:end_marker].strip()
            
            elif '{' in response and '}' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
            
            if json_str:
                metrics = json.loads(json_str)
                print(f"Parsed metrics keys: {list(metrics.keys())}")  
                
                meets_thresholds = True
                failed_thresholds = []
                
                for key, threshold in self.thresholds.items():
                    if key in metrics:
                        if metrics[key] < threshold:
                            meets_thresholds = False
                            failed_thresholds.append(f"{key}: {metrics[key]} < {threshold}")
                
                metrics['meets_thresholds'] = meets_thresholds
                metrics['failed_thresholds'] = failed_thresholds
                
                print(f"Threshold check - Meets all: {meets_thresholds}") 
                if failed_thresholds:
                    print(f"Failed thresholds: {failed_thresholds}") 
                
                logger.info("Conversation analysis completed successfully")
                return metrics
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.error(f"Error parsing metrics: {e}")
            print(f"Raw response: {response}")  
            return self._default_metrics()
    
    def _default_metrics(self) -> Dict[str, Any]:
        try:
            default_metrics = {
                "professionalism_score": 0,
                "script_adherence_score": 0,
                "negotiation_effectiveness": 0,
                "objection_handling_score": 0,
                "resolution_success_rate": 0,
                "repetition_issues": 100,
                "relevance_score": 0,
                "conversation_length": 0,
                "customer_satisfaction": 0,
                "compliance_score": 0,
                "overall_performance": 0,
                "meets_thresholds": False,
                "areas_for_improvement": ["analysis failed"],
                "strengths": []
            }
            logger.warning("Using default metrics due to analysis failure")
            return default_metrics
        except Exception as e:
            logger.error(f"Error creating default metrics: {e}")
            return {}