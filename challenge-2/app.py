import requests
import json
import time
import random
from dataclasses import dataclass
from typing import List, Dict, Any
import time

class DebtCollectionPrompt:
    @staticmethod
    def generate_system_instructions(user_name: str, due_amount: float, 
                                     days_overdue: int) -> str:
        """Generate system instructions for the debt collection agent"""
        return f"""
You are a polite and professional customer service agent named Sarah from 
Riverline Bank. You are calling to remind about an overdue credit card bill.
IMPORTANT GUIDELINES:
- Begin the call immediately with the greeting. Do NOT say "okay here we go" or any filler.
- Keep the tone courteous, respectful, and natural—not robotic.
- ALWAYS remain polite, even if the customer is rude or aggressive.
- Use the customer's name sparingly - only when confirming identity and closing the call.
CUSTOMER DETAILS:
- Name: {user_name}
- Due Amount: ₹{due_amount:,.2f}
- Days Overdue: {days_overdue} days
OPENING LINE (use exactly this):
"Hello, This is Sarah calling from Riverline Bank regarding your credit card bill. 
May i speak with {user_name}?"
CONVERSATION FLOW:
1. Confirm if you're speaking with the correct person.
2. Say: "I'm calling to remind you that your credit card bill of ₹{due_amount:,.2f} 
is currently {days_overdue} days overdue."
3. Ask: "Are you able to make the payment today?"
RESPONSE SCENARIOS:
IF CUSTOMER AGREES TO PAY:
- Say: "Thank you so much for confirming. We really appreciate it. Have a wonderful day!"
- End the call politely.
IF CUSTOMER SAYS THEY CANNOT PAY RIGHT NOW:
- Say: "I understand. Would you be able to make the payment within the next 3 days? We can
 extend your deadline by 3 more days."
- Wait for their response.
IF CUSTOMER STILL CANNOT PAY AFTER EXTENSION OFFER:
- Say: "I completely understand your situation. Our human agent will be calling you shortly
 to help rectify this matter and discuss available options. Thank you for your time."
- End the call politely.
IF CUSTOMER IS RUDE OR AGGRESSIVE:
- Remain calm and polite.
- Say: "I understand this might be frustrating. I'm here to help find a solution that 
works for you."
- Continue with the appropriate scenario above.
IF CUSTOMER WANTS TO END THE CALL:
- Say: "Thank you for your time. Have a great day!"
- End the call immediately.
TONE GUIDELINES:
- Always calm, friendly, and professional
- Never aggressive, pushy, or confrontational
- Show empathy and understanding
- Keep responses concise and clear
COMPLIANCE NOTES:
- Do not discuss transaction history or account details
- Never mention penalties, legal actions, or consequences
- Respect the customer's requests and responses
- Focus only on payment confirmation and assistance
GOAL: Politely remind about the overdue bill, confirm payment intentions, offer reasonable 
extensions, and maintain positive customer relationships while being helpful and understanding.
"""

@dataclass
class CustomerPersona:
    name: str
    personality: str
    scenario: str
    expected_behavior: str

@dataclass
class TestMetrics:
    is_repeating: bool = False
    is_negotiating_enough: bool = False
    provides_irrelevant_responses: bool = False
    maintains_professionalism: bool = True
    follows_script: bool = True
    handles_objections_well: bool = True
    conversation_length: int = 0
    successful_resolution: bool = False

class GeminiAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini API"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"API Error: {e}")
            return "Sorry, I'm having technical difficulties."

class CustomerPersonaGenerator:
    @staticmethod
    def generate_personas() -> List[CustomerPersona]:
        """Generate different customer personas for testing"""
        personas = [
            CustomerPersona(
                name="Rajesh Kumar",
                personality="cooperative_but_struggling",
                scenario="Recently lost job, wants to pay but needs time",
                expected_behavior="Polite, explains situation, asks for extension"
            ),
            CustomerPersona(
                name="Priya Sharma",
                personality="aggressive_defensive",
                scenario="Frustrated with bank, claims payment was made",
                expected_behavior="Angry, confrontational, disputes the debt"
            ),
            CustomerPersona(
                name="Amit Patel",
                personality="avoidant_evasive",
                scenario="Tries to avoid payment, makes excuses",
                expected_behavior="Evasive, changes subject, tries to end call quickly"
            ),
            CustomerPersona(
                name="Sunita Reddy",
                personality="confused_elderly",
                scenario="Elderly customer, confused about the debt",
                expected_behavior="Slow to understand, asks many questions, needs clarification"
            ),
            CustomerPersona(
                name="Vikram Singh",
                personality="cooperative_immediate",
                scenario="Ready to pay immediately",
                expected_behavior="Agrees quickly, wants to resolve immediately"
            ),
            CustomerPersona(
                name="Meera Joshi",
                personality="bargaining_negotiator",
                scenario="Wants to negotiate payment terms and amount",
                expected_behavior="Asks for discounts, partial payments, extended deadlines"
            )
        ]
        return personas

class ConversationSimulator:
    def __init__(self, api_key: str):
        self.gemini = GeminiAPI(api_key)
        self.personas = CustomerPersonaGenerator.generate_personas()
    
    def create_customer_prompt(self, persona: CustomerPersona, agent_message: str, conversation_history: List[str]) -> str:
        """Create prompt for customer persona"""
        history = '\n'.join(conversation_history[-6:])  # Last 6 exchanges for context
        
        return f"""
You are {persona.name}, a credit card customer with the following characteristics:
- Personality: {persona.personality}
- Scenario: {persona.scenario}
- Expected behavior: {persona.expected_behavior}

IMPORTANT: You are receiving a call from a debt collection agent. Respond naturally as this character would.

Previous conversation:
{history}

Agent just said: "{agent_message}"

Respond as {persona.name} would in this situation. Keep responses realistic and conversational (1-3 sentences max).
Do not break character or mention that you are roleplaying.
"""
    
    def simulate_conversation(self, persona: CustomerPersona, max_turns: int = 10) -> Dict[str, Any]:
        """Simulate a full conversation between agent and customer"""
        
        # Generate random debt details
        due_amount = random.uniform(5000, 50000)
        days_overdue = random.randint(7, 60)
        
        # Initialize conversation
        conversation_history = []
        agent_prompt = DebtCollectionPrompt.generate_system_instructions(
            persona.name, due_amount, days_overdue
        )
        
        print(f"\n--- Simulating conversation with {persona.name} ({persona.personality}) ---")
        print(f"Debt: ₹{due_amount:,.2f}, {days_overdue} days overdue")
        
        # Agent starts the conversation
        agent_message = self.gemini.generate_response(
            agent_prompt + "\n\nStart the conversation with your opening line."
        )
        
        conversation_history.append(f"Agent: {agent_message}")
        print(f"Agent: {agent_message}")
        
        for turn in range(max_turns):
            # Customer responds
            customer_prompt = self.create_customer_prompt(persona, agent_message, conversation_history)
            customer_message = self.gemini.generate_response(customer_prompt)
            
            conversation_history.append(f"Customer: {customer_message}")
            print(f"Customer ({persona.name}): {customer_message}")
            
            # Check if conversation should end
            if any(phrase in customer_message.lower() for phrase in ["goodbye", "bye", "hang up", "end call"]):
                break
            
            # Agent responds
            agent_context = f"""
{agent_prompt}

Previous conversation:
{chr(10).join(conversation_history[-8:])}

Customer just said: "{customer_message}"

Respond according to your instructions. If the conversation seems complete, politely end it.
"""
            
            agent_message = self.gemini.generate_response(agent_context)
            conversation_history.append(f"Agent: {agent_message}")
            print(f"Agent: {agent_message}")
            
            # Check if agent ended conversation
            if any(phrase in agent_message.lower() for phrase in ["have a great day", "thank you for your time", "goodbye"]):
                break
            
            time.sleep(1)  # Rate limiting
        
        return {
            'persona': persona,
            'conversation': conversation_history,
            'debt_details': {'amount': due_amount, 'days_overdue': days_overdue}
        }

class MetricsAnalyzer:
    def __init__(self):
        self.repetitive_phrases = ["as i mentioned", "like i said", "again", "once again"]
        self.professional_phrases = ["thank you", "i understand", "i appreciate", "please"]
        self.irrelevant_keywords = ["weather", "sports", "politics", "unrelated"]
    
    def analyze_conversation(self, conversation_data: Dict[str, Any]) -> TestMetrics:
        """Analyze conversation and calculate metrics"""
        conversation = conversation_data['conversation']
        agent_messages = [msg for msg in conversation if msg.startswith("Agent:")]
        
        metrics = TestMetrics()
        
        # 1. Check if bot is repeating itself
        metrics.is_repeating = self._check_repetition(agent_messages)
        
        # 2. Check if bot is negotiating enough
        metrics.is_negotiating_enough = self._check_negotiation(agent_messages)
        
        # 3. Check for irrelevant responses
        metrics.provides_irrelevant_responses = self._check_relevance(agent_messages)
        
        # 4. Check professionalism
        metrics.maintains_professionalism = self._check_professionalism(agent_messages)
        
        # 5. Check script adherence
        metrics.follows_script = self._check_script_adherence(agent_messages, conversation_data)
        
        # 6. Check objection handling
        metrics.handles_objections_well = self._check_objection_handling(conversation)
        
        # 7. Conversation length
        metrics.conversation_length = len(conversation)
        
        # 8. Successful resolution
        metrics.successful_resolution = self._check_resolution(conversation)
        
        return metrics
    
    def _check_repetition(self, agent_messages: List[str]) -> bool:
        """Check if agent is repeating phrases"""
        all_text = ' '.join(agent_messages).lower()
        repetition_count = sum(all_text.count(phrase) for phrase in self.repetitive_phrases)
        return repetition_count > 2
    
    def _check_negotiation(self, agent_messages: List[str]) -> bool:
        """Check if agent offers alternatives/extensions"""
        negotiation_phrases = ["3 days", "extension", "deadline", "payment plan", "options"]
        all_text = ' '.join(agent_messages).lower()
        return any(phrase in all_text for phrase in negotiation_phrases)
    
    def _check_relevance(self, agent_messages: List[str]) -> bool:
        """Check for irrelevant responses"""
        all_text = ' '.join(agent_messages).lower()
        return any(keyword in all_text for keyword in self.irrelevant_keywords)
    
    def _check_professionalism(self, agent_messages: List[str]) -> bool:
        """Check if agent maintains professional tone"""
        all_text = ' '.join(agent_messages).lower()
        professional_count = sum(all_text.count(phrase) for phrase in self.professional_phrases)
        return professional_count >= 2
    
    def _check_script_adherence(self, agent_messages: List[str], conversation_data: Dict[str, Any]) -> bool:
        """Check if agent follows the script"""
        first_message = agent_messages[0].lower() if agent_messages else ""
        return "riverline bank" in first_message and "credit card bill" in first_message
    
    def _check_objection_handling(self, conversation: List[str]) -> bool:
        """Check how well agent handles customer objections"""
        customer_messages = [msg for msg in conversation if msg.startswith("Customer:")]
        agent_responses = [msg for msg in conversation if msg.startswith("Agent:")]
        
        if len(customer_messages) < 2:
            return True
        
        # Look for empathetic responses after customer objections
        empathy_phrases = ["understand", "appreciate", "help", "solution"]
        
        for i, customer_msg in enumerate(customer_messages[1:], 1):
            if any(word in customer_msg.lower() for word in ["can't", "cannot", "don't have", "frustrated"]):
                if i < len(agent_responses):
                    agent_response = agent_responses[i].lower()
                    if any(phrase in agent_response for phrase in empathy_phrases):
                        return True
        
        return False
    
    def _check_resolution(self, conversation: List[str]) -> bool:
        """Check if conversation reached a resolution"""
        last_few_messages = ' '.join(conversation[-3:]).lower()
        resolution_phrases = ["thank you", "great day", "human agent will call", "appreciate it"]
        return any(phrase in last_few_messages for phrase in resolution_phrases)

class VoiceAgentTester:
    def __init__(self, api_key: str):
        self.simulator = ConversationSimulator(api_key)
        self.analyzer = MetricsAnalyzer()
    
    def run_comprehensive_test(self, num_tests_per_persona: int = 2) -> Dict[str, Any]:
        """Run comprehensive testing across all personas"""
        print("🚀 Starting Voice Agent Testing Platform")
        print("=" * 60)
        
        all_results = []
        persona_results = {}
        
        for persona in self.simulator.personas:
            persona_tests = []
            print(f"\n📞 Testing with persona: {persona.name} ({persona.personality})")
            
            for test_num in range(num_tests_per_persona):
                print(f"\n--- Test {test_num + 1} for {persona.name} ---")
                
                # Simulate conversation
                conversation_data = self.simulator.simulate_conversation(persona)
                
                # Analyze metrics
                metrics = self.analyzer.analyze_conversation(conversation_data)
                
                test_result = {
                    'persona': persona.name,
                    'personality': persona.personality,
                    'conversation': conversation_data['conversation'],
                    'metrics': metrics,
                    'debt_details': conversation_data['debt_details']
                }
                
                persona_tests.append(test_result)
                all_results.append(test_result)
                
                # Print metrics for this test
                self._print_test_metrics(test_result, test_num + 1)
            
            persona_results[persona.name] = persona_tests
        
        # Generate summary report
        summary = self._generate_summary_report(all_results)
        
        return {
            'all_results': all_results,
            'persona_results': persona_results,
            'summary': summary
        }
    
    def _print_test_metrics(self, test_result: Dict[str, Any], test_num: int):
        """Print metrics for a single test"""
        metrics = test_result['metrics']
        print(f"\n📊 Test {test_num} Metrics for {test_result['persona']}:")
        print(f"   ✅ Maintains Professionalism: {metrics.maintains_professionalism}")
        print(f"   ✅ Follows Script: {metrics.follows_script}")
        print(f"   ✅ Negotiates Appropriately: {metrics.is_negotiating_enough}")
        print(f"   ❌ Is Repeating: {metrics.is_repeating}")
        print(f"   ❌ Provides Irrelevant Responses: {metrics.provides_irrelevant_responses}")
        print(f"   ✅ Handles Objections Well: {metrics.handles_objections_well}")
        print(f"   📏 Conversation Length: {metrics.conversation_length} exchanges")
        print(f"   🎯 Successful Resolution: {metrics.successful_resolution}")
    
    def _generate_summary_report(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive summary report"""
        total_tests = len(all_results)

        # Calculate aggregate metrics
        professionalism_score = sum(r['metrics'].maintains_professionalism for r in all_results) / total_tests * 100
        script_adherence_score = sum(r['metrics'].follows_script for r in all_results) / total_tests * 100
        negotiation_score = sum(r['metrics'].is_negotiating_enough for r in all_results) / total_tests * 100
        repetition_rate = sum(r['metrics'].is_repeating for r in all_results) / total_tests * 100
        irrelevant_response_rate = sum(r['metrics'].provides_irrelevant_responses for r in all_results) / total_tests * 100
        objection_handling_score = sum(r['metrics'].handles_objections_well for r in all_results) / total_tests * 100
        resolution_rate = sum(r['metrics'].successful_resolution for r in all_results) / total_tests * 100
        avg_conversation_length = sum(r['metrics'].conversation_length for r in all_results) / total_tests
        
        # Performance by persona
        persona_performance = {}
        for result in all_results:
            persona = result['persona']
            if persona not in persona_performance:
                persona_performance[persona] = []
            persona_performance[persona].append(result['metrics'])
        
        summary = {
            'total_tests': total_tests,
            'professionalism_score': professionalism_score,
            'script_adherence_score': script_adherence_score,
            'negotiation_score': negotiation_score,
            'repetition_rate': repetition_rate,
            'irrelevant_response_rate': irrelevant_response_rate,
            'objection_handling_score': objection_handling_score,
            'resolution_rate': resolution_rate,
            'avg_conversation_length': avg_conversation_length,
            'persona_performance': persona_performance
        }
        
        return summary
    
    def print_final_report(self, results: Dict[str, Any]):
        """Print comprehensive final report"""
        summary = results['summary']
        
        print("\n" + "=" * 80)
        print("🎯 VOICE AGENT TESTING SUMMARY REPORT")
        print("=" * 80)
        
        print(f"\n📈 OVERALL PERFORMANCE METRICS:")
        print(f"   Total Tests Conducted: {summary['total_tests']}")
        print(f"   Professionalism Score: {summary['professionalism_score']:.1f}%")
        print(f"   Script Adherence Score: {summary['script_adherence_score']:.1f}%")
        print(f"   Negotiation Effectiveness: {summary['negotiation_score']:.1f}%")
        print(f"   Objection Handling Score: {summary['objection_handling_score']:.1f}%")
        print(f"   Successful Resolution Rate: {summary['resolution_rate']:.1f}%")
        print(f"   Average Conversation Length: {summary['avg_conversation_length']:.1f} exchanges")
        
        print(f"\n⚠️  AREAS FOR IMPROVEMENT:")
        print(f"   Repetition Rate: {summary['repetition_rate']:.1f}% (Lower is better)")
        print(f"   Irrelevant Response Rate: {summary['irrelevant_response_rate']:.1f}% (Lower is better)")
        
        print(f"\n🎭 PERFORMANCE BY CUSTOMER PERSONA:")
        for persona, metrics_list in summary['persona_performance'].items():
            avg_prof = sum(m.maintains_professionalism for m in metrics_list) / len(metrics_list) * 100
            avg_resolution = sum(m.successful_resolution for m in metrics_list) / len(metrics_list) * 100
            print(f"   {persona}: {avg_prof:.1f}% professional, {avg_resolution:.1f}% resolution rate")
        
        print("\n" + "=" * 80)

# Main execution
def main():
    # Configuration
    GOOGLE_API_KEY = "AIzaSyDRSGM-6OyP0BwEuhnFn_II0CwdeQYK1Lw"
    
    # Initialize tester
    tester = VoiceAgentTester(GOOGLE_API_KEY)
    
    # Run comprehensive tests
    results = tester.run_comprehensive_test(num_tests_per_persona=1)  # Reduced for demo
    
    # Print final report
    tester.print_final_report(results)
    
    # Optional: Save results to file
    with open('voice_agent_test_results.json', 'w') as f:
        # Convert metrics objects to dict for JSON serialization
        serializable_results = results.copy()
        for result in serializable_results['all_results']:
            result['metrics'] = result['metrics'].__dict__
        json.dump(serializable_results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to 'voice_agent_test_results.json'")

if __name__ == "__main__":
    main()