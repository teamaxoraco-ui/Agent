# 🌍 AI Voice Agent - Visa Consultant

An AI-powered phone receptionist for **Axoraco Visa Consultants**. Callers can book appointments, get visa information, and request callbacks - all through natural voice conversation.

## 🚀 Live Demo

**Call:** Your Twilio Number  
**Powered by:** Deepgram AI + Twilio

## Features

- 📅 **Book Appointments** - Schedule visa consultations
- ℹ️ **Visa Information** - Get requirements & fees for any visa type
- 🔄 **Manage Bookings** - Check, reschedule, or cancel appointments
- 📞 **Request Callback** - Get a consultant to call you back

## Visa Types Supported

| Type | Consultation Fee | Processing Time |
|------|-----------------|-----------------|
| Tourist | $50 | 5-15 days |
| Student | $75 | 2-8 weeks |
| Work | $100 | 4-12 weeks |
| Business | $75 | 1-4 weeks |
| Immigration | $150 | Varies |

## Quick Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Environment Variables
```
DEEPGRAM_API_KEY=your_key_here
```

## Project Structure

```
├── main.py                    # WebSocket server
├── config.json                # AI personality & functions
├── appointment_functions.py   # Booking & info handlers
├── Dockerfile                 # Container config
└── requirements.txt           # Dependencies
```

## Customization

- **Business Name:** Edit `config.json` → `instructions`
- **Services:** Modify `VISA_INFO` in `appointment_functions.py`
- **Hours:** Update `BUSINESS_HOURS` dictionary

---

Built with ❤️ by **Axoraco**
