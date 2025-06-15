# Challenge 2: Self-correcting Voice Agents

## Overview
 Testing voice agents and implementing self-correction mechanisms for different types of failure scenarios. When a metric fails during a session, the agent intelligently updates its prompt to adapt and respond more accurately in future interactions.
## Tech Stack
- **Gemini** - AI conversational model
- **Python** - Implementation with ruff linting

## Demo

### Screenshots

#### Metrics Failing for a user
![LiveKit Dashboard](https://github.com/Mamlesh18/Riverline-Hiring-Assignement/blob/main/challenge-2/example/output_1.png)


#### Self-Correction Triggered After Metric Failure

![AWS S3 Storage]([screenshot-url-here](https://github.com/Mamlesh18/Riverline-Hiring-Assignement/blob/main/challenge-2/example/output_2.png))



## Commands

### Run Development
```bash
python agent_testing.py
```


## File Structure
```
├── agent_testing.py      # Main file to run and configure LiveKit sessions
├── config.py             # Environment variables and settings
├── prompt.py             # Custom prompt logic (e.g., credit card reminders)
├── log.py                # Logging utility
├── json_saving.py        # Real-time transcription and data saving logic
├── metrics_analyser.py   # Real-time metric analysis and prompt adjustment
```
## Code Standards
- Strict ruff linting
- Virtual environment (venv)

## Setup
1. Create and activate a virtual environment.
2. Install required dependencies using pip.
3. Configure your environment variables in config.py.
4. Run the agent using the command provided above.
