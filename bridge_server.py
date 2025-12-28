# bridge_server.py
# WebSocket bridge sending emotional data + voice data to p5.js

import asyncio
import json
import websockets
import sys

# --- WINDOWS FIX (Prevents "GetQueuedCompletionStatus" crash) ---
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# ----------------------------------------------------------------

# Global references
emotion_engine = None
voice_engine = None

async def send_loop(websocket):
    """Continuously send emotion JSON to the browser."""
    print("Web client connected.")

    while True:
        # Sleep to prevent CPU freeze
        await asyncio.sleep(0.10)  

        if emotion_engine is None:
            continue

        frame = emotion_engine.latest_frame
        if frame is None:
            continue

        # Get voice data safely
        volume = 0.0
        words = ""
        if voice_engine:
            volume = voice_engine.get_volume()
            words = voice_engine.voice_last_text

        payload = {
            "dominant": frame.dominant,
            "valence": float(frame.valence),
            "arousal": float(frame.arousal),
            "emotions": frame.all_emotions,
            "volume": volume,
            "words": words,
            "_t": int(asyncio.get_event_loop().time() * 1000)
        }

        try:
            await websocket.send(json.dumps(payload))
        except Exception:
            print("Web client disconnected.")
            break

async def server_main(port=8765):
    print(f"Starting WebSocket server at ws://localhost:{port}")
    async with websockets.serve(send_loop, "localhost", port):
        await asyncio.Future()  # run forever

def start_bridge(emotion, voice=None, port=8765):
    global emotion_engine, voice_engine
    emotion_engine = emotion
    voice_engine = voice

    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.create_task(server_main(port=port))
    loop.run_forever()

if __name__ == "__main__":
    asyncio.run(server_main())