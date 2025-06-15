import asyncio
import json
import os
import re
from datetime import datetime

from config import DebtCollectionConfig


class TranscriptionManager:
    def __init__(self, session_id: str, phone_number: str, debtor_name: str, 
                 debt_amount: float, days_overdue: int):
        self.transcript_data = {
            "session_id": session_id,
            "call_details": {
                "phone_number": phone_number,
                "debtor_name": debtor_name,
                "debt_amount": debt_amount,
                "days_overdue": days_overdue,
                "call_start_time": datetime.now().isoformat()
            },
            "real_time_transcript": [],
            "conversation_items": [],
            "clean_conversation": []  # New clean format
        }
        self.debtor_name = debtor_name
        self.phone_number = phone_number
    
    def extract_clean_content(self, content_str):
        """Extract clean content from the content string"""
        try:
            # Handle different content formats
            if isinstance(content_str, list):
                return ' '.join(str(item) for item in content_str)
            
            content_str = str(content_str)
            
            # Extract content from the string format
            # Look for content=['...'] pattern
            content_match = re.search(r"content=\['([^']+)'\]", content_str)
            if content_match:
                return content_match.group(1).replace('\\n', '').strip()
            
            # Look for content=["..."] pattern  
            content_match = re.search(r'content=\["([^"]+)"\]', content_str)
            if content_match:
                return content_match.group(1).replace('\\n', '').strip()
            
            # If no pattern matches, return the original string
            return content_str.strip()
            
        except Exception as e:
            print(f"Error extracting content: {e}")
            return str(content_str)
    
    def log_conversation_item(self, event):
        """Log conversation items as they're added"""
        try:
            role = getattr(event.item, 'role', 'unknown')
            content = self.extract_clean_content(str(event.item))
            
            # Add to detailed log
            item_data = {
                "timestamp": datetime.now().isoformat(),
                "type": event.item.type if hasattr(event.item, 'type') else "unknown",
                "content": str(event.item),
                "role": role
            }
            self.transcript_data["conversation_items"].append(item_data)
            
            # Add to clean conversation format
            clean_item = {
                "speaker": "agent" if role == "assistant" else "user",
                "message": content,
                "timestamp": datetime.now().isoformat()
            }
            self.transcript_data["clean_conversation"].append(clean_item)
            
            # Print clean format
            speaker_label = "Agent" if role == "assistant" else "User"
            print(f"[{speaker_label}]: {content}")
            
        except Exception as e:
            print(f"Error logging conversation item: {e}")
    
    def log_user_transcription(self, event):
        """Log user speech transcription in real-time"""
        try:
            text_content = None
            if hasattr(event, 'text'):
                text_content = event.text
            elif hasattr(event, 'transcript'):
                text_content = event.transcript
            elif hasattr(event, 'content'):
                text_content = event.content
            else:
                text_content = str(event)
            
            transcription_data = {
                "timestamp": datetime.now().isoformat(),
                "speaker": "user",
                "text": text_content,
                "is_final": getattr(event, 'is_final', True),
                "event_type": type(event).__name__
            }
            self.transcript_data["real_time_transcript"].append(transcription_data)
            
            # Only print final transcriptions to avoid spam
            if getattr(event, 'is_final', True):
                print(f"[USER SPEECH]: {text_content}")
                
        except Exception as e:
            print(f"Error logging user transcription: {e}")
    
    def generate_simple_transcript(self):
        """Generate simple transcript format"""
        simple_transcript = []
        
        for item in self.transcript_data["clean_conversation"]:
            speaker = item["speaker"].capitalize()
            message = item["message"]
            simple_transcript.append(f"{speaker}: {message}")
        
        return "\n".join(simple_transcript)
    
    async def save_transcript(self, session=None):
        """Save complete transcript"""
        try:
            current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            self.transcript_data["call_details"]["call_end_time"] = (
                datetime.now().isoformat())
            self.transcript_data["call_details"]["call_duration"] = str(
                datetime.now() - datetime.fromisoformat(
                    self.transcript_data["call_details"]["call_start_time"]
                )
            )
            
            # Try to get session history if available
            if session:
                try:
                    if hasattr(session, 'history'):
                        self.transcript_data["complete_history"] = session.history.to_dict()
                except Exception as history_error:
                    print(f"Could not get session history: {history_error}")
            
            # Generate safe filename
            safe_name = re.sub(r'[^\w\-_\.]', '_', self.debtor_name)
            filename = (
                f"transcript_{safe_name}_"
                f"{self.phone_number.replace('+', '')}_{current_date}.json"
            )
            
            # Also save a simple text version
            simple_filename = (
                f"simple_transcript_{safe_name}_"
                f"{self.phone_number.replace('+', '')}_{current_date}.txt"
            )
            
            # Create transcript directory and file paths
            transcript_dir = os.path.join(os.getcwd(), 
                                          DebtCollectionConfig.TRANSCRIPT_DIR)
            filepath = os.path.join(transcript_dir, filename)
            simple_filepath = os.path.join(transcript_dir, simple_filename)
            
            os.makedirs(transcript_dir, exist_ok=True)
            
            # Save detailed transcript
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.transcript_data, f, indent=2, ensure_ascii=False)
            
            # Save simple transcript
            simple_content = self.generate_simple_transcript()
            with open(simple_filepath, 'w', encoding='utf-8') as f:
                f.write("Call Details:\n")
                f.write(f"Debtor: {self.debtor_name}\n")
                f.write(f"Phone: {self.phone_number}\n")
                f.write(f"Amount: ₹{self.transcript_data['call_details']['debt_amount']}\n")
                f.write(f"Days Overdue: {self.transcript_data['call_details']['days_overdue']}\n")
                f.write(f"\n{'='*50}\n")
                f.write("CONVERSATION:\n")
                f.write(f"{'='*50}\n\n")
                f.write(simple_content)
            
            print(f"✅ Transcript saved: {filepath}")
            print(f"✅ Simple transcript saved: {simple_filepath}")
            
            # Print the clean conversation to console
            print(f"\n{'='*50}")
            print("FINAL CONVERSATION SUMMARY:")
            print(f"{'='*50}")
            print(simple_content)
            print(f"{'='*50}\n")
            
        except Exception as e:
            print(f"❌ Error saving transcript: {e}")
            import traceback
            print(f"Full error: {traceback.format_exc()}")
    
    def setup_session_listeners(self, session):
        """Setup event listeners for the session"""
        session.on("conversation_item_added", self.log_conversation_item)
        session.on("user_input_transcribed", self.log_user_transcription)
    
    async def start_periodic_save(self, session=None):
        """Start periodic transcript saving"""
        while True:
            try:
                await asyncio.sleep(DebtCollectionConfig.TRANSCRIPT_SAVE_INTERVAL)
                print("💾 Saving periodic transcript backup...")
                await self.save_transcript(session)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️ Periodic save error: {e}")
    
    def create_session_end_handler(self, session=None):
        """Create session end handler"""
        def on_session_end(event):
            print("📝 Session ending, saving transcript...")
            asyncio.create_task(self.save_transcript(session))
        
        return on_session_end