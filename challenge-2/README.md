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

### Video Demo
[Add video URL here]

*Voice agent handling credit card payment reminder conversation with natural speech processing*

### Screenshots

#### LiveKit Agent Dashboard
![LiveKit Dashboard](screenshot-url-here)

*LiveKit agent dashboard showing active sessions, connection status, and real-time processing metrics*

#### AWS S3 Audio Storage
![AWS S3 Storage](screenshot-url-here)

*AWS S3 bucket with saved audio recordings organized by timestamp for conversation retrieval and analysis*

#### LiveKit Transcript Conversation
![Transcript Log](screenshot-url-here)

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

### File Details

#### `agent.py`
Main LiveKit agent configuration with audio processing and AI integration

#### `config.py`
Environment variable loading and configuration management

#### `prompt.py`
Custom prompts for credit card payment reminder conversations

#### `log.py`
Logging system for debugging and monitoring

#### `transcription.py`
Real-time transcription saving and conversation storage

## Features
- Real-time speech processing
- Natural conversation flow
- Audio recording storage
- Transcript logging
- Payment reminder automation

## Code Standards
- Strict ruff linting
- Virtual environment (venv)
- LiveKit documentation compliance
- Optimized implementation

## Setup
1. Install dependencies in venv
2. Configure environment variables
3. Run with commands above

Built following LiveKit documentation and community best practices.