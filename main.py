"""
AI Voice Agent - Main Server

A real-time AI Voice Agent using Python, Twilio, and Deepgram.
This server bridges Twilio phone calls with Deepgram's AI agent API.

Architecture:
    Caller -> Twilio -> This Server -> Deepgram -> Response -> Twilio -> Caller

Usage:
    1. Start ngrok: ngrok http 5000
    2. Update Twilio TwiML Bin with ngrok URL
    3. Run: python main.py
    4. Call your Twilio number
"""

import asyncio
import base64
import json
import os
import logging
from typing import Optional

import websockets
from websockets.server import WebSocketServerProtocol
from dotenv import load_dotenv

from pharmacy_functions import execute_function

# =============================================================================
# CONFIGURATION
# =============================================================================

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
PORT = int(os.getenv("PORT", 5000))
HOST = os.getenv("HOST", "0.0.0.0")  # 0.0.0.0 for cloud deployment

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# DEEPGRAM CONNECTION
# =============================================================================

async def connect_to_deepgram() -> Optional[websockets.WebSocketClientProtocol]:
    """
    Establish a WebSocket connection to Deepgram's Agent API.
    
    Returns:
        WebSocket connection to Deepgram, or None if connection fails
    """
    if not DEEPGRAM_API_KEY:
        logger.error("DEEPGRAM_API_KEY not found in environment variables!")
        return None
    
    url = "wss://agent.deepgram.com/agent"
    headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}"}
    
    try:
        connection = await websockets.connect(url, extra_headers=headers)
        logger.info("✅ Connected to Deepgram Agent API")
        return connection
    except Exception as e:
        logger.error(f"❌ Failed to connect to Deepgram: {e}")
        return None


# =============================================================================
# TWILIO HANDLER
# =============================================================================

async def handle_twilio_connection(twilio_ws: WebSocketServerProtocol):
    """
    Handle an incoming WebSocket connection from Twilio.
    
    This function:
    1. Connects to Deepgram
    2. Sends the agent configuration
    3. Bridges audio between Twilio and Deepgram
    4. Handles function calls from the AI
    
    Args:
        twilio_ws: WebSocket connection from Twilio
    """
    logger.info("📞 New call connected from Twilio")
    
    # Connect to Deepgram
    deepgram_ws = await connect_to_deepgram()
    if not deepgram_ws:
        logger.error("Cannot proceed without Deepgram connection")
        return
    
    # Load and send configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        await deepgram_ws.send(json.dumps(config))
        logger.info("📋 Sent configuration to Deepgram")
    except FileNotFoundError:
        logger.error("config.json not found!")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Invalid config.json: {e}")
        return

    # Track stream ID for Twilio responses
    stream_sid = None
    
    # -------------------------------------------------------------------------
    # TASK: Receive audio from Twilio and forward to Deepgram
    # -------------------------------------------------------------------------
    async def twilio_to_deepgram():
        nonlocal stream_sid
        try:
            async for message in twilio_ws:
                data = json.loads(message)
                event_type = data.get('event')
                
                if event_type == 'start':
                    # Call started - capture stream ID
                    stream_sid = data.get('streamSid')
                    logger.info(f"🎙️ Stream started: {stream_sid}")
                
                elif event_type == 'media':
                    # Audio data from caller
                    payload = data['media']['payload']
                    # Decode from base64 to raw bytes for Deepgram
                    audio_bytes = base64.b64decode(payload)
                    await deepgram_ws.send(audio_bytes)
                
                elif event_type == 'stop':
                    logger.info("📴 Call ended")
                    break
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("Twilio connection closed")
        except Exception as e:
            logger.error(f"Error in twilio_to_deepgram: {e}")
    
    # -------------------------------------------------------------------------
    # TASK: Receive responses from Deepgram and forward to Twilio
    # -------------------------------------------------------------------------
    async def deepgram_to_twilio():
        try:
            async for message in deepgram_ws:
                # Binary message = audio data
                if isinstance(message, bytes):
                    # Encode to base64 for Twilio
                    audio_b64 = base64.b64encode(message).decode('utf-8')
                    
                    # Send to Twilio
                    twilio_message = {
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {
                            "payload": audio_b64
                        }
                    }
                    await twilio_ws.send(json.dumps(twilio_message))
                
                # Text message = control/function call
                else:
                    data = json.loads(message)
                    msg_type = data.get('type')
                    
                    if msg_type == 'Welcome':
                        logger.info("🤝 Deepgram session established")
                    
                    elif msg_type == 'ConversationText':
                        # Log conversation for debugging
                        role = data.get('role', 'unknown')
                        content = data.get('content', '')
                        logger.info(f"💬 {role.upper()}: {content}")
                    
                    elif msg_type == 'FunctionCallRequest':
                        # AI wants to call a function!
                        function_name = data.get('function_name')
                        function_call_id = data.get('function_call_id')
                        parameters = data.get('input', {})
                        
                        logger.info(f"🔧 Function call: {function_name}({parameters})")
                        
                        # Execute the function
                        result = execute_function(function_name, parameters)
                        logger.info(f"📤 Function result: {result}")
                        
                        # Send result back to Deepgram
                        response = {
                            "type": "FunctionCallResponse",
                            "function_call_id": function_call_id,
                            "output": result
                        }
                        await deepgram_ws.send(json.dumps(response))
                    
                    elif msg_type == 'AgentThinking':
                        logger.debug("🤔 Agent is thinking...")
                    
                    elif msg_type == 'Error':
                        logger.error(f"❌ Deepgram error: {data}")
                        
        except websockets.exceptions.ConnectionClosed:
            logger.info("Deepgram connection closed")
        except Exception as e:
            logger.error(f"Error in deepgram_to_twilio: {e}")
    
    # -------------------------------------------------------------------------
    # Run both tasks concurrently
    # -------------------------------------------------------------------------
    try:
        await asyncio.gather(
            twilio_to_deepgram(),
            deepgram_to_twilio()
        )
    finally:
        # Cleanup
        if deepgram_ws:
            await deepgram_ws.close()
        logger.info("🔌 Call session ended")


# =============================================================================
# ROUTING
# =============================================================================

async def router(websocket: WebSocketServerProtocol, path: str):
    """
    Route incoming WebSocket connections based on path.
    
    Args:
        websocket: The incoming WebSocket connection
        path: The request path
    """
    logger.info(f"🌐 Connection on path: {path}")
    
    if path == "/twilio" or path == "/":
        await handle_twilio_connection(websocket)
    else:
        logger.warning(f"Unknown path: {path}")
        await websocket.close()


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Start the WebSocket server."""
    logger.info(f"""
╔══════════════════════════════════════════════════════════════╗
║               AI Voice Agent Server                          ║
║                                                              ║
║  🚀 Starting server on ws://{HOST}:{PORT}                    ║
║                                                              ║
║  Next steps:                                                 ║
║  1. Run: ngrok http {PORT}                                   ║
║  2. Update Twilio TwiML Bin with ngrok URL                   ║
║  3. Call your Twilio number!                                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    async with websockets.serve(router, HOST, PORT):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Server stopped by user")
