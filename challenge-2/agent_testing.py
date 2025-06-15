import time
import random
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

from config import config
from log import logger
from prompt import DebtCollectionPrompt
from json_saving import json_saver
from metrics_analyser import GeminiAPI, MetricsAnalyzer
from adaptive_prompt import AdaptivePromptManager

@dataclass
class CustomerPersona:
    name: str
    personality: str
    scenario: str
 
class ConversationSimulator:
    def __init__(self, api_key: str):
        try:
            self.gemini = GeminiAPI(api_key)
            self.personas = self._generate_personas()
            self.metrics_analyzer = MetricsAnalyzer(api_key)
            logger.info("ConversationSimulator initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ConversationSimulator: {e}")
            raise
    
    def _generate_personas(self) -> List[CustomerPersona]:
        try:
            personas = [
                CustomerPersona("Rajesh Kumar", "cooperative_but_struggling", "Recently lost job, wants to pay but needs time"),
                CustomerPersona("Priya Sharma", "aggressive_defensive", "Frustrated with bank, claims payment was made"),
                CustomerPersona("Amit Patel", "avoidant_evasive", "Tries to avoid payment, makes excuses"),
                CustomerPersona("Sita Devi", "calm_responsive", "Willing to pay, asks for deadline extension"),
                CustomerPersona("Ravi Singh", "confused_uninformed", "Unaware of overdue payment, needs explanation"),
            ]
            logger.info(f"Generated {len(personas)} customer personas")
            return personas
        except Exception as e:
            logger.error(f"Error generating personas: {e}")
            return []
    
    def create_customer_prompt(self, persona: CustomerPersona, agent_message: str, conversation_history: List[str]) -> str:
        try:
            history = '\n'.join(conversation_history[-6:])
            
            prompt = f"""
You are {persona.name} with personality: {persona.personality}
Scenario: {persona.scenario}
Previous conversation:
{history}
Agent just said: "{agent_message}"
Respond naturally as this character (1-2 sentences max). Stay in character.
"""
            logger.debug(f"Created customer prompt for {persona.name}")
            return prompt
        except Exception as e:
            logger.error(f"Error creating customer prompt: {e}")
            return ""
    
    def simulate_conversation(self, persona: CustomerPersona, max_turns: int = 10) -> Dict[str, Any]:
        try:
            due_amount = random.uniform(5000, 50000)
            days_overdue = random.randint(7, 60)
            
            conversation_history = []
            agent_prompt = DebtCollectionPrompt.generate_system_instructions(persona.name, due_amount, days_overdue)
            
            print(f"\n--- Conversation with {persona.name} ({persona.personality}) ---")
            print(f"Debt: ₹{due_amount:,.2f}, {days_overdue} days overdue")
            
            time.sleep(2)  
            start_prompt = agent_prompt + "\n\nStart the conversation with your opening line."
            agent_message = self.gemini.generate_response(start_prompt)
            
            conversation_history.append(f"Agent: {agent_message}")
            print(f"Agent: {agent_message}")
            
            for turn in range(max_turns):
                time.sleep(2) 
                customer_prompt = self.create_customer_prompt(persona, agent_message, conversation_history)
                customer_message = self.gemini.generate_response(customer_prompt)
                
                conversation_history.append(f"Customer: {customer_message}")
                print(f"Customer ({persona.name}): {customer_message}")
                
                customer_end_phrases = [
                    "goodbye", "bye", "hang up", "end call", "thank you", "thanks", 
                    "that's fine", "okay", "alright", "sounds good", "i understand"
                ]
                
                if any(phrase in customer_message.lower() for phrase in customer_end_phrases):
                    if any(word in customer_message.lower() for word in ["fine", "okay", "alright", "understand", "good"]):
                        time.sleep(2)
                        final_agent_prompt = f"""
{agent_prompt}
Previous conversation:
{chr(10).join(conversation_history[-8:])}
Customer just said: "{customer_message}" 
The customer seems to have accepted your solution/explanation. Provide a polite closing statement and end the call professionally.
"""
                        agent_message = self.gemini.generate_response(final_agent_prompt)
                        conversation_history.append(f"Agent: {agent_message}")
                        print(f"Agent: {agent_message}")
                        break
                    elif "goodbye" in customer_message.lower() or "bye" in customer_message.lower():
                        break
                
                time.sleep(2)  
                agent_context = f"""
{agent_prompt}
Previous conversation:
{chr(10).join(conversation_history[-8:])}
Customer just said: "{customer_message}"
Respond according to your instructions. If the customer seems satisfied or if you've provided a complete solution, politely end the call.
"""
                
                agent_message = self.gemini.generate_response(agent_context)
                conversation_history.append(f"Agent: {agent_message}")
                print(f"Agent: {agent_message}")
                
                agent_end_phrases = [
                    "have a great day", "have a good day", "thank you for your time", 
                    "goodbye", "have a wonderful day", "take care", "my colleague will call",
                    "human agent will call", "someone will be in touch"
                ]
                
                if any(phrase in agent_message.lower() for phrase in agent_end_phrases):
                    print("🔚 Agent ended the conversation")
                    break
            
            print("Analyzing conversation metrics...")
            persona_info = {
                'personality': persona.personality,
                'scenario': persona.scenario,
                'name': persona.name
            }
            
            metrics = self.metrics_analyzer.analyze_conversation(conversation_history, persona_info)
            
            result = {
                'persona': persona.name,
                'personality': persona.personality,
                'scenario': persona.scenario,
                'conversation_history': conversation_history,
                'debt_details': {'amount': due_amount, 'days_overdue': days_overdue},
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Conversation simulation completed for {persona.name}")
            return result
            
        except Exception as e:
            logger.error(f"Error simulating conversation with {persona.name}: {e}")
            return {}

class VoiceAgentTester:
    def __init__(self, api_key: str):
        try:
            self.simulator = ConversationSimulator(api_key)
            self.adaptive_manager = AdaptivePromptManager()  # Add this line
            logger.info("VoiceAgentTester initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing VoiceAgentTester: {e}")
            raise
    
    def run_test_suite(self, num_tests_per_persona: int = 1, max_retries: int = 3) -> Dict[str, Any]:
        try:
            print("🚀 Starting Voice Agent Testing")
            print("=" * 50)
            
            all_results = []
            
            for persona in self.simulator.personas:
                print(f"\n📞 Testing with {persona.name}")
                
                # Track attempts for this persona
                attempt = 0
                persona_passed = False
                
                while attempt < max_retries and not persona_passed:
                    attempt += 1
                    print(f"Attempt {attempt} for {persona.name}")
                    
                    if attempt > 1:
                        time.sleep(2)
                    
                    result = self.simulator.simulate_conversation(persona)
                    metrics = result['metrics']
                    
                    # Display metrics
                    self._display_metrics(persona.name, metrics)
                    
                    if metrics.get('meets_thresholds', False):
                        print(f"✅ {persona.name} PASSED on attempt {attempt}")
                        persona_passed = True
                        all_results.append(result)
                        break
                    else:
                        print(f"❌ {persona.name} FAILED attempt {attempt}")
                        failed_thresholds = metrics.get('failed_thresholds', [])
                        
                        if attempt < max_retries:
                            print(f"🔄 Updating prompt for {persona.name}...")
                            failed_metrics = self.adaptive_manager.analyze_failures(failed_thresholds)
                            improvements = self.adaptive_manager.generate_improvements(failed_metrics)
                            
                            # Update the prompt in DebtCollectionPrompt
                            original_prompt = DebtCollectionPrompt.generate_system_instructions(
                                persona.name, result['debt_details']['amount'], 
                                result['debt_details']['days_overdue']
                            )
                            updated_prompt = self.adaptive_manager.update_prompt(original_prompt, improvements)
                            
                            # Temporarily store the updated prompt
                            DebtCollectionPrompt._temp_updated_prompt = updated_prompt
                            print(f"📝 Prompt updated with {len(improvements)} improvements")
                        else:
                            print(f"⚠️ {persona.name} failed all {max_retries} attempts")
                            all_results.append(result)
                
                # Clean up temporary prompt
                if hasattr(DebtCollectionPrompt, '_temp_updated_prompt'):
                    delattr(DebtCollectionPrompt, '_temp_updated_prompt')
                
                print("-" * 60)
            
            summary = self._generate_summary(all_results)
            
            final_results = {
                'test_summary': summary,
                'individual_results': all_results,
                'test_timestamp': datetime.now().isoformat(),
                'total_conversations': len(all_results)
            }
            
            logger.info(f"Test suite completed with {len(all_results)} conversations")
            return final_results
            
        except Exception as e:
            logger.error(f"Error running test suite: {e}")
            return {}
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            if not results:
                return {}
            
            total_tests = len(results)
            
            avg_professionalism = sum(r['metrics'].get('professionalism_score', 0) for r in results) / total_tests
            avg_script_adherence = sum(r['metrics'].get('script_adherence_score', 0) for r in results) / total_tests
            avg_negotiation = sum(r['metrics'].get('negotiation_effectiveness', 0) for r in results) / total_tests
            avg_objection_handling = sum(r['metrics'].get('objection_handling_score', 0) for r in results) / total_tests
            avg_resolution = sum(r['metrics'].get('resolution_success_rate', 0) for r in results) / total_tests
            avg_overall = sum(r['metrics'].get('overall_performance', 0) for r in results) / total_tests
            
            threshold_pass_rate = sum(r['metrics'].get('meets_thresholds', False) for r in results) / total_tests * 100
            
            summary = {
                'total_tests': total_tests,
                'average_scores': {
                    'professionalism': round(avg_professionalism, 2),
                    'script_adherence': round(avg_script_adherence, 2),
                    'negotiation_effectiveness': round(avg_negotiation, 2),
                    'objection_handling': round(avg_objection_handling, 2),
                    'resolution_success': round(avg_resolution, 2),
                    'overall_performance': round(avg_overall, 2)
                },
                'threshold_pass_rate': round(threshold_pass_rate, 2)
            }
            
            logger.info("Summary generated successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {}
    
    def print_summary(self, results: Dict[str, Any]):
        try:
            summary = results['test_summary']
            
            print("\n" + "=" * 60)
            print("📊 FINAL TEST SUMMARY")
            print("=" * 60)
            
            print(f"Total Conversations: {summary['total_tests']}")
            print(f"Threshold Pass Rate: {summary['threshold_pass_rate']}%")
            
            print("\n📈 Average Scores:")
            for metric, score in summary['average_scores'].items():
                print(f"  {metric.replace('_', ' ').title()}: {score}/100")
            
            print("\n💾 Detailed results saved to JSON file")
            logger.info("Summary printed successfully")
            
        except Exception as e:
            logger.error(f"Error printing summary: {e}")
            print("Error displaying summary")
    def _display_metrics(self, persona_name: str, metrics: Dict[str, Any]):
        """Helper method to display metrics"""
        print(f"\n📊 DETAILED METRICS for {persona_name}:")
        print(f"   Professionalism Score: {metrics.get('professionalism_score', 0)}/100")
        print(f"   Script Adherence: {metrics.get('script_adherence_score', 0)}/100") 
        print(f"   Negotiation Effectiveness: {metrics.get('negotiation_effectiveness', 0)}/100")
        print(f"   Objection Handling: {metrics.get('objection_handling_score', 0)}/100")
        print(f"   Resolution Success: {metrics.get('resolution_success_rate', 0)}/100")
        print(f"   Repetition Issues: {metrics.get('repetition_issues', 0)}/100 (lower is better)")
        print(f"   Relevance Score: {metrics.get('relevance_score', 0)}/100")
        print(f"   Conversation Length: {metrics.get('conversation_length', 0)} exchanges")
        print(f"   Customer Satisfaction: {metrics.get('customer_satisfaction', 0)}/100")
        print(f"   Compliance Score: {metrics.get('compliance_score', 0)}/100")
        print(f"   Overall Performance: {metrics.get('overall_performance', 0)}/100")
        print(f"   Meets Thresholds: {metrics.get('meets_thresholds', False)}")
        
        if 'failed_thresholds' in metrics and metrics['failed_thresholds']:
            print(f"   ❌ Failed Thresholds: {metrics['failed_thresholds']}")
        
        if 'strengths' in metrics:
            print(f"   ✅ Strengths: {metrics['strengths']}")
            
        if 'areas_for_improvement' in metrics:
            print(f"   🔧 Areas for Improvement: {metrics['areas_for_improvement']}")
def main():
    try:
        tester = VoiceAgentTester(config.api_key)
        
        results = tester.run_test_suite(num_tests_per_persona=1, max_retries=3)
        
        tester.print_summary(results)
        
        filepath = json_saver.save_results(results)
        
        print(f"\n📄 Results saved to '{filepath}'")
        logger.info("Main execution completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()