"""
AI Voice Agent - Main Server

A real-time AI Voice Agent using Python, Twilio, and Deepgram.
This server bridges Twilio phone calls with Deepgram's AI agent API.

Architecture:
    Caller -> Twilio -> This Server -> Deepgram -> Response -> Twilio -> Caller
"""

import asyncio
import base64
import json
import os
import logging
from aiohttp import web, WSMsgType
import aiohttp

from appointment_functions import execute_function

# =============================================================================
# CONFIGURATION
# =============================================================================

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
PORT = int(os.getenv("PORT", 5000))
HOST = os.getenv("HOST", "0.0.0.0")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# HEALTH CHECK (for Render)
# =============================================================================

async def health_check(request):
    """HTTP health check endpoint for Render."""
    return web.Response(text="OK", status=200)


async def index(request):
    """Root endpoint."""
    return web.Response(
        text="AI Voice Agent Server - WebSocket endpoint at /twilio",
        status=200
    )


# =============================================================================
# DEEPGRAM CONNECTION
# =============================================================================

async def connect_to_deepgram():
    """Establish a WebSocket connection to Deepgram's Agent API."""
    if not DEEPGRAM_API_KEY:
        logger.error("DEEPGRAM_API_KEY not found!")
        return None
    
    try:
        session = aiohttp.ClientSession()
        ws = await session.ws_connect(
            "wss://agent.deepgram.com/agent",
            headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}
        )
        logger.info("✅ Connected to Deepgram Agent API")
        return ws, session
    except Exception as e:
        logger.error(f"❌ Failed to connect to Deepgram: {e}")
        return None, None


# =============================================================================
# TWILIO WEBSOCKET HANDLER
# =============================================================================

async def twilio_websocket_handler(request):
    """Handle WebSocket connection from Twilio."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    logger.info("📞 New call connected from Twilio")
    
    # Connect to Deepgram
    result = await connect_to_deepgram()
    if result[0] is None:
        await ws.close()
        return ws
    
    deepgram_ws, session = result
    
    # Load and send configuration
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        await deepgram_ws.send_json(config)
        logger.info("📋 Sent configuration to Deepgram")
    except Exception as e:
        logger.error(f"Config error: {e}")
        await ws.close()
        return ws

    stream_sid = None
    
    async def receive_from_twilio():
        nonlocal stream_sid
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    event_type = data.get('event')
                    
                    if event_type == 'start':
                        stream_sid = data.get('streamSid')
                        logger.info(f"🎙️ Stream started: {stream_sid}")
                    
                    elif event_type == 'media':
                        payload = data['media']['payload']
                        audio_bytes = base64.b64decode(payload)
                        await deepgram_ws.send_bytes(audio_bytes)
                    
                    elif event_type == 'stop':
                        logger.info("📴 Call ended")
                        break
                        
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
                    break
        except Exception as e:
            logger.error(f"Error receiving from Twilio: {e}")
    
    async def receive_from_deepgram():
        try:
            async for msg in deepgram_ws:
                if msg.type == WSMsgType.BINARY:
                    # Audio from Deepgram
                    audio_b64 = base64.b64encode(msg.data).decode('utf-8')
                    await ws.send_json({
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {"payload": audio_b64}
                    })
                
                elif msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    msg_type = data.get('type')
                    
                    if msg_type == 'Welcome':
                        logger.info("🤝 Deepgram session established")
                    
                    elif msg_type == 'ConversationText':
                        role = data.get('role', 'unknown')
                        content = data.get('content', '')
                        logger.info(f"💬 {role.upper()}: {content}")
                    
                    elif msg_type == 'FunctionCallRequest':
                        function_name = data.get('function_name')
                        function_call_id = data.get('function_call_id')
                        parameters = data.get('input', {})
                        
                        logger.info(f"🔧 Function call: {function_name}({parameters})")
                        result = execute_function(function_name, parameters)
                        logger.info(f"📤 Function result: {result}")
                        
                        await deepgram_ws.send_json({
                            "type": "FunctionCallResponse",
                            "function_call_id": function_call_id,
                            "output": result
                        })
                    
                    elif msg_type == 'Error':
                        logger.error(f"❌ Deepgram error: {data}")
                        
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"Deepgram WS error: {deepgram_ws.exception()}")
                    break
        except Exception as e:
            logger.error(f"Error receiving from Deepgram: {e}")
    
    try:
        await asyncio.gather(
            receive_from_twilio(),
            receive_from_deepgram()
        )
    finally:
        await deepgram_ws.close()
        await session.close()
        logger.info("🔌 Call session ended")
    
    return ws


# =============================================================================
# MAIN
# =============================================================================

def create_app():
    """Create the aiohttp application."""
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/health', health_check)
    app.router.add_get('/twilio', twilio_websocket_handler)
    return app


if __name__ == "__main__":
    logger.info(f"""
╔══════════════════════════════════════════════════════════════╗
║               AI Voice Agent Server                          ║
║                                                              ║
║  🚀 Starting server on http://{HOST}:{PORT}                  ║
║  📡 WebSocket endpoint: /twilio                              ║
║  💚 Health check: /health                                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    app = create_app()
    web.run_app(app, host=HOST, port=PORT)
