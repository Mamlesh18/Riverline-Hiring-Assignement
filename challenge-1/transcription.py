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
            "conversation_items": []
        }
        self.debtor_name = debtor_name
        self.phone_number = phone_number
    
    def log_conversation_item(self, event):
        """Log conversation items as they're added"""
        try:
            item_data = {
                "timestamp": datetime.now().isoformat(),
                "type": event.item.type if hasattr(event.item, 'type') else "unknown",
                "content": str(event.item),
                "role": getattr(event.item, 'role', 'unknown')
            }
            self.transcript_data["conversation_items"].append(item_data)
            print(f"[CONVERSATION] {item_data['role']}: {item_data['content']}")
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
            print(f"[USER SPEECH]: {text_content}")
        except Exception as e:
            print(f"Error logging user transcription: {e}")
            print(f"Event attributes: {dir(event)}")
    
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
                        self.transcript_data["complete_history"] =(
                             session.history.to_dict())
                except Exception as history_error:
                    print(f"Could not get session history: {history_error}")
            
            # Generate safe filename
            safe_name = re.sub(r'[^\w\-_\.]', '_', self.debtor_name)
            filename = (
                f"transcript_{safe_name}_"
                f"{self.phone_number.replace('+', '')}_{current_date}.json"
            )
            
            # Create transcript directory and file path
            transcript_dir = os.path.join(os.getcwd(), 
                                          DebtCollectionConfig.TRANSCRIPT_DIR)
            filepath = os.path.join(transcript_dir, filename)
            
            os.makedirs(transcript_dir, exist_ok=True)
            
            # Save transcript
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.transcript_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Transcript saved: {filepath}")
            
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