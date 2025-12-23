# 🤖 AI Voice Agent

A real-time AI Voice Agent using **Python**, **Twilio**, and **Deepgram**. Customers call a phone number and interact with an AI-powered pharmacy assistant.

## 🚀 Quick Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Architecture

```
Caller → Twilio → This Server → Deepgram AI → Response → Twilio → Caller
```

## Setup

### 1. Deploy to Render.com
1. Fork this repo
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Add environment variable: `DEEPGRAM_API_KEY`
5. Deploy!

### 2. Configure Twilio
Create a TwiML Bin with:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Connecting you to the AI Assistant.</Say>
    <Connect>
        <Stream url="wss://YOUR-RENDER-URL.onrender.com/twilio" />
    </Connect>
</Response>
```

Set your Twilio phone number to use this TwiML Bin.

### 3. Call Your Number! 📞

## Project Structure

```
├── main.py                 # WebSocket server
├── config.json             # AI agent configuration
├── pharmacy_functions.py   # Custom tools
├── Dockerfile              # Container config
├── render.yaml             # Render deployment
└── requirements.txt        # Dependencies
```

## Customization

- **AI Personality:** Edit `config.json` → `agent.think.instructions`
- **Add Functions:** Add to `pharmacy_functions.py` and register in `config.json`

---

Built with ❤️ by **Axoraco**
