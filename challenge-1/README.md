# Challenge 1: Building Voice Agents with LiveKit

## Overview
Voice agent built using LiveKit integration with Deepgram STT/TTS and Gemini AI for credit card payment reminders.

## Tech Stack
- **LiveKit** - Voice agent platform
- **Deepgram** - Speech-to-Text & Text-to-Speech
- **Gemini** - AI conversational model
- **AWS S3** - Audio storage
- **Python** - Implementation with ruff linting

## Demo

#### Voice Agent with LiveKit Video Demo
<p align="center">
  <video src="images/video.mp4" width="500px"></video>
</p>

<video src="video-recordings/challenge_1.mp4" width="320" height="240" controls></video>

![non working video](video-recordings/challenge_1.mp4)

*LiveKit agent dashboard showing active sessions, connection status, and real-time processing metrics*

#### AWS S3 Audio Storage
![AWS S3 Storage](https://github.com/Mamlesh18/Riverline-Hiring-Assignement/blob/main/challenge-1/example/aws.png)

*AWS S3 bucket with saved audio recordings organized by timestamp for conversation retrieval and analysis*

#### LiveKit Transcript Conversation
![Transcript Log](https://github.com/Mamlesh18/Riverline-Hiring-Assignement/blob/main/challenge-1/example/output_1.png)

*Real-time conversation transcript with timestamps, speaker identification, and customer metadata*

#### Voice Agent with LiveKit Audio Demo
<audio controls>
  <source src="https://github.com/Mamlesh18/Riverline-Hiring-Assignement/raw/main/challenge-1/audio-recordings/recording_1.mp3" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>

*Real-time conversation transcript with timestamps, speaker identification, and customer metadata*

## Commands

### Run Development
```bash
python agent.py dev
```

### Deploy Agent
```bash
lk dispatch create --new-room --agent-name telephony-agent --metadata '{"phone_number": "+917358580180", "name": "Rajesh Kumar", "amount": 15000, "days_overdue": 45}'
```

## File Structure
```
├── agent.py          # Main LiveKit configuration
├── config.py         # Environment variables and settings
├── prompt.py         # Custom prompts for credit card reminders
├── log.py            # Logging system
├── transcription.py  # Real-time transcription handling
```

## Features
- Real-time STT with deepgram
- Natural conversation flow with deepgram TTS with
- Audio recording storage in AWS S3 Bucket
- Transcript logging in json file
- Payment reminder automation call scheudling

## Code Standards
- Strict ruff linting
- Virtual environment (venv)
- LiveKit documentation compliance

## Setup
1. Install dependencies in venv
2. Configure environment variables
3. Run with commands above

Built following LiveKit documentation and community best practices.
