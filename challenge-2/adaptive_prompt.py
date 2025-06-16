from typing import List

from log import logger


class AdaptivePromptManager:
    def __init__(self):
        self.improvement_strategies = {
            'negotiation_effectiveness': [
                "When customer cannot pay immediately, ALWAYS offer specific alternatives: "
                "'Would you prefer to pay 50% now and 50% in 7 days, or would a full payment in 5"
                 " days work better for you?'",
                "Use empathetic negotiation: 'I understand this is challenging. Let me see what "
                "options we have available to help you.'",
                "Provide multiple payment options: partial payments, extended deadlines, or payment"
                "plans."
            ],
            'resolution_success_rate': [
                "ALWAYS end with concrete next steps: 'So to confirm, you'll make the payment by "
                "[specific date]. I'll send you a confirmation SMS shortly.'",
                "Ask for commitment: 'Can I have your confirmation that this "
                "timeline works for you?'",
                "Establish clear follow-up: 'I'll call you on [specific date] to confirm the "
                "payment was processed.'"
            ],
            'objection_handling_score': [
                "When customer objects, first acknowledge: 'I completely understand your "
                "concern about...'",
                "Provide solutions, not just policies: 'Let me see how we can work together"
                " to resolve this.'",
                "Never argue with customers - redirect to solutions instead."
            ],
            'customer_satisfaction': [
                "Use more empathetic language: 'I can hear this is stressful for you.'",
                "Offer genuine help: 'I'm here to find a solution that works for your situation.'",
                "Thank customers for their cooperation throughout the call."
            ],
            'professionalism_score': [
                "Maintain calm, respectful tone even when customer is upset.",
                "Use please and thank you appropriately.",
                "Never interrupt the customer while they're speaking."
            ]
        }
    
    def analyze_failures(self, failed_thresholds: List[str]) -> List[str]:
        """Extract metric names from failed thresholds"""
        try:
            failed_metrics = []
            for threshold in failed_thresholds:
                metric_name = threshold.split(':')[0].strip()
                failed_metrics.append(metric_name)
            logger.info(f"Identified failed metrics: {failed_metrics}")
            return failed_metrics
        except Exception as e:
            logger.error(f"Error analyzing failures: {e}")
            return []
    
    def generate_improvements(self, failed_metrics: List[str]) -> List[str]:
        """Generate improvement instructions based on failed metrics"""
        try:
            improvements = []
            for metric in failed_metrics:
                if metric in self.improvement_strategies:
                    improvements.extend(self.improvement_strategies[metric])
            
            logger.info(f"Generated {len(improvements)} improvement strategies")
            return improvements
        except Exception as e:
            logger.error(f"Error generating improvements: {e}")
            return []
    
    def update_prompt(self, base_prompt: str, improvements: List[str]) -> str:
        """Add improvement instructions to the base prompt"""
        try:
            if not improvements:
                return base_prompt
            
            improvement_section = "\n\nIMPROVED INSTRUCTIONS (CRITICAL - FOLLOW THESE):\n"
            for i, improvement in enumerate(improvements, 1):
                improvement_section += f"{i}. {improvement}\n"
            
            goal_index = base_prompt.find("GOAL:")
            if goal_index != -1:
                updated_prompt = base_prompt[:
                                             goal_index] + improvement_section + "\n" + base_prompt[
                                                 goal_index:]
            else:
                updated_prompt = base_prompt + improvement_section
            
            logger.info("Prompt updated with improvements")
            print("Updated prompt",updated_prompt)
            return updated_prompt
        except Exception as e:
            logger.error(f"Error updating prompt: {e}")
            return base_prompt