# 🤖 AI Voice Agent

A real-time AI Voice Agent using **Python**, **Twilio**, and **Deepgram**. Customers call a phone number and interact with an AI-powered pharmacy assistant.

## Architecture

```
Caller → Twilio → This Server → Deepgram AI → Response → Twilio → Caller
```

## Quick Start

### 1. Prerequisites

- Python 3.9+
- [Deepgram Account](https://deepgram.com) (free $200 credit)
- [Twilio Account](https://twilio.com) + Phone Number (~$1.15)
- [ngrok](https://ngrok.com) (free)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your DEEPGRAM_API_KEY
```

### 4. Configure Twilio

1. Go to **Twilio Console** → **Developer Tools** → **TwiML Bins**
2. Create a new bin named "Voice Agent" with this XML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Connecting you to the AI Assistant.</Say>
    <Connect>
        <Stream url="wss://YOUR-NGROK-URL.ngrok-free.app/twilio" />
    </Connect>
</Response>
```

3. Go to **Phone Numbers** → **Manage** → **Active Numbers**
4. Set "A Call Comes In" → **TwiML Bin** → Select your bin

### 5. Run

Terminal 1:
```bash
ngrok http 5000
```

Terminal 2:
```bash
python main.py
```

Update your TwiML Bin with the ngrok URL, then **call your Twilio number!**

## Project Structure

```
├── main.py                 # WebSocket server (Twilio ↔ Deepgram bridge)
├── config.json             # AI agent configuration
├── pharmacy_functions.py   # Custom tools the AI can use
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Customization

### Change the AI Personality

Edit `config.json` → `agent.think.instructions`

### Add New Functions

1. Add function to `pharmacy_functions.py`
2. Register in `execute_function()` dispatcher
3. Add schema to `config.json` → `agent.think.functions`

## Built with ❤️ by Axoraco
