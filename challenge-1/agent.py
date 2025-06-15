import asyncio
import json
import re

from livekit import agents, api
from livekit.agents import Agent, AgentSession
from livekit.plugins import deepgram, google, silero

from config import DebtCollectionConfig
from log import logger
from prompt import DebtCollectionPrompt
from transcription import TranscriptionManager


class DebtCollectionAssistant(Agent):
    def __init__(self, user_name: str, due_amount: float,
                  days_overdue: int = 5) -> None:
        instructions = DebtCollectionPrompt.generate_system_instructions(
            user_name, due_amount, days_overdue
        )
        
        super().__init__(instructions=instructions)
        self.debtor_name = user_name
        self.debt_amount = due_amount
        self.days_overdue = days_overdue
        self.call_attempts = 0
        self.payment_commitment = None

def parse_metadata(metadata_str: str):
    """Parse metadata from job context"""
    phone_number = DebtCollectionConfig.DEFAULT_PHONE_NUMBER
    debtor_name = DebtCollectionConfig.DEFAULT_DEBTOR_NAME
    debt_amount = DebtCollectionConfig.DEFAULT_DEBT_AMOUNT
    days_overdue = DebtCollectionConfig.DEFAULT_DAYS_OVERDUE
    
    if not metadata_str:
        return phone_number, debtor_name, debt_amount, days_overdue
    
    try:
        
        if metadata_str.startswith('{'):
            try:
                if metadata_str.endswith('}'):
                    metadata = json.loads(metadata_str)
                else:
                    fixed_metadata = metadata_str
                    if not fixed_metadata.endswith('}'):
                        fixed_metadata += '}'
                    
                    fixed_metadata = re.sub(r'(\w+):', r'"\1":', fixed_metadata)
                    fixed_metadata = re.sub(r':\s*([^",}]+)(?=[,}])', r': "\1"',
                                             fixed_metadata)
                    
                    metadata = json.loads(fixed_metadata)
                
                phone_number = metadata.get("phone_number", phone_number)
                debtor_name = metadata.get("name", debtor_name)
                debt_amount = float(metadata.get("amount", debt_amount))
                days_overdue = int(metadata.get("days_overdue", days_overdue))
                
                
            except (json.JSONDecodeError, ValueError):
                phone_match = re.search(r'phone_number["\s]*:["\s]*([+\d]+)',
                                         metadata_str)
                name_match = re.search(r'name["\s]*:["\s]*([^,"}]+)', metadata_str)
                amount_match = re.search(r'amount["\s]*:["\s]*([0-9.]+)', metadata_str)
                days_match = re.search(r'days_overdue["\s]*:["\s]*([0-9]+)',
                                        metadata_str)
                
                if phone_match:
                    phone_number = phone_match.group(1)
                if name_match:
                    debtor_name = name_match.group(1).strip('"').strip()
                if amount_match:
                    debt_amount = float(amount_match.group(1))
                if days_match:
                    days_overdue = int(days_match.group(1))
                    
        else:
            phone_number = metadata_str
            
    except Exception as e:
        logger.error(f"Failed to parse metadata: {e}")
    return phone_number, debtor_name, debt_amount, days_overdue

async def create_session():
    """Create and configure the agent session"""
    try:
        logger.info("Creating agent session with configured models")
        
        session = AgentSession(
            stt=deepgram.STT(
                model=DebtCollectionConfig.STT_MODEL,
                language=DebtCollectionConfig.STT_LANGUAGE,
                smart_format=DebtCollectionConfig.STT_SMART_FORMAT,
                punctuate=DebtCollectionConfig.STT_PUNCTUATE
            ),
            llm=google.LLM(
                model=DebtCollectionConfig.LLM_MODEL,
                temperature=DebtCollectionConfig.LLM_TEMPERATURE,  
            ),
            tts=deepgram.TTS(
                model=DebtCollectionConfig.TTS_MODEL,
            ),
            vad=silero.VAD.load(
                min_silence_duration=DebtCollectionConfig.VAD_MIN_SILENCE_DURATION
            ),
        )
        
        logger.info("Agent session created successfully")
        return session
        
    except Exception as e:
        logger.error(f"Failed to create agent session: {e}")
        raise

async def make_sip_call(ctx, phone_number, debtor_name):
    """Make SIP call with retry logic"""
    max_retries = DebtCollectionConfig.MAX_RETRIES
    retry_delay = DebtCollectionConfig.RETRY_DELAY
    
    for attempt in range(max_retries + 1):
        try:
            
            sip_participant = await ctx.api.sip.create_sip_participant(
                api.CreateSIPParticipantRequest(
                    room_name=ctx.room.name,
                    sip_trunk_id=DebtCollectionConfig.SIP_TRUNK_ID,
                    sip_call_to=phone_number,
                    participant_identity="debt_collection_call",
                    participant_name=f"Collection Call - {debtor_name}",
                    wait_until_answered=True,
                    play_dialtone=False
                )
            )
            return sip_participant
            
        except Exception as call_error:
            if attempt < max_retries:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  
            else:
                raise call_error

async def entrypoint(ctx: agents.JobContext):
    req = api.RoomCompositeEgressRequest(
        room_name=ctx.room.name,
        audio_only=True,
        file_outputs=[api.EncodedFileOutput(
            file_type=api.EncodedFileType.OGG,
            filepath=f"livekit/debt-collection-{ctx.room.name}-{int(asyncio.get_event_loop().time())}.ogg",
            s3=api.S3Upload(
                bucket=DebtCollectionConfig.S3_BUCKET,
                region=DebtCollectionConfig.S3_REGION,
                access_key=DebtCollectionConfig.S3_ACCESS_KEY,
                secret=DebtCollectionConfig.S3_SECRET_KEY,
            ),
        )],
    )
    
    lkapi = api.LiveKitAPI()
    try:
        res = await lkapi.egress.start_room_composite_egress(req)
        logger.info(f"Recording started with egress ID: {res.egress_id}")
    except Exception as e:
        logger.error(f"Failed to start recording: {e}")
        # Continue without recording rather than failing completely
    finally:
        await lkapi.aclose()
    await ctx.connect()
    
    DebtCollectionConfig.validate_config()
    
    metadata_str = ctx.job.metadata.strip() if ctx.job.metadata else ""
    phone_number, debtor_name, debt_amount, days_overdue = parse_metadata(metadata_str)
    

    session = await create_session()
    
    transcript_manager = TranscriptionManager(
        session_id=ctx.room.name,
        phone_number=phone_number,
        debtor_name=debtor_name,
        debt_amount=debt_amount,
        days_overdue=days_overdue
    )
    
    transcript_manager.setup_session_listeners(session)
    
    session_end_handler = transcript_manager.create_session_end_handler(session)
    session.on("session_ended", session_end_handler)
    session.on("agent_disconnected", session_end_handler)
    
    ctx.add_shutdown_callback(lambda: transcript_manager.save_transcript(session))
    
    debt_agent = DebtCollectionAssistant(
        user_name=debtor_name,
        due_amount=debt_amount,
        days_overdue=days_overdue
    )
    
    await session.start(
        room=ctx.room,
        agent=debt_agent,
    )
    
    
    try:
        await make_sip_call(ctx, phone_number, debtor_name)
        
        await asyncio.wait_for(
            asyncio.sleep(DebtCollectionConfig.INITIAL_SLEEP), 
            timeout=DebtCollectionConfig.CONNECTION_TIMEOUT
        )
        
        greeting_instructions = DebtCollectionPrompt.generate_greeting_instructions(
            debtor_name)
        await session.generate_reply(instructions=greeting_instructions)
        
        
        asyncio.create_task(transcript_manager.start_periodic_save(session))
        
        await asyncio.sleep(2)
        await transcript_manager.save_transcript(session)
        
    except asyncio.TimeoutError:
        await transcript_manager.save_transcript(session)
        try:
            await session.close()
        except Exception:
            pass
        
    except Exception as e:
        await transcript_manager.save_transcript(session)
        try:
            await session.close()
        except Exception:
            pass
        raise e

if __name__ == "__main__":
    try:
        logger.info("Starting debt collection telephony agent...")
        agents.cli.run_app(agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="telephony-agent"  
        ))
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        raise