import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Response, BackgroundTasks
from dotenv import load_dotenv

from ai_engine import process_customer_message
from whatsapp_client import send_whatsapp_message

load_dotenv()

app = FastAPI(title="WhatsApp AI Booking Assistant")

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "my_secure_verify_token_123")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "WhatsApp AI Salon Assistant",
        "vertical": "Hair & Beauty Lounge"
    }

@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Webhook Verification for WhatsApp Cloud API.
    Meta sends a GET request with hub.mode, hub.verify_token, and hub.challenge.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        print("[SUCCESS] Webhook verified successfully by Meta!")
        return Response(content=challenge, media_type="text/plain")
    
    print(f"[ERROR] Verification failed. Received token: {token}, Expected: {WHATSAPP_VERIFY_TOKEN}")
    raise HTTPException(status_code=403, detail="Verification token mismatch")

async def handle_incoming_message_task(from_number: str, message_body: str):
    """
    Background worker: Processes message with AI and replies via WhatsApp Cloud API.
    """
    print(f"\n📩 [INCOMING] From {from_number}: {message_body}")
    
    # 1. Process message through AI engine
    reply_text = await process_customer_message(from_number, message_body)
    print(f"🤖 [AI REPLY] To {from_number}:\n{reply_text}\n")
    
    # 2. Send the reply back to the customer on WhatsApp
    await send_whatsapp_message(to_number=from_number, message_text=reply_text)

@app.post("/webhook")
async def handle_whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receives incoming webhook payloads from Meta.
    Returns HTTP 200 immediately to Meta, and handles the AI reply in the background.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    if body.get("object") == "whatsapp_business_account":
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                # Check for incoming customer messages
                if "messages" in value:
                    for message in value["messages"]:
                        from_number = message.get("from")
                        message_type = message.get("type")
                        
                        if message_type == "text":
                            user_text = message["text"].get("body", "")
                            # Schedule background response so Meta gets immediate 200 OK
                            background_tasks.add_task(handle_incoming_message_task, from_number, user_text)
                            
                        elif message_type == "audio":
                            print(f"[AUDIO] Voice note received from {from_number} (Phase 2 capability)")
                            background_tasks.add_task(
                                send_whatsapp_message, 
                                from_number, 
                                "Thank you for your voice note! We are reviewing it and will respond right away. 🙏"
                            )
                            
        return {"status": "success"}

    return {"status": "ignored"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
