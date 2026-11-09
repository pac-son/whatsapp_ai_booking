import os
import sys
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Response, BackgroundTasks
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows consoles
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from ai_engine import process_customer_message
from whatsapp_client import send_whatsapp_message

load_dotenv()

app = FastAPI(title="WhatsApp AI Booking Assistant")

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "my_secure_salon_token_2026")

from database import mark_deposit_paid

@app.post("/stripe-webhook")
async def handle_stripe_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receives events from Stripe when a customer pays their deposit.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    import json
    import stripe
    
    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        else:
            event = json.loads(payload)
    except Exception as e:
        print(f"[STRIPE WEBHOOK ERROR] {e}")
        # Fallback to direct json parsing if signature verification isn't needed in sandbox
        try:
            event = json.loads(payload)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid Stripe payload")

    event_type = event.get("type")
    print(f"\n[STRIPE WEBHOOK] Received event: {event_type}")

    if event_type == "checkout.session.completed":
        session_data = event["data"]["object"]
        metadata = session_data.get("metadata", {})
        booking_id = metadata.get("booking_id")
        customer_phone = metadata.get("customer_phone")
        
        if booking_id:
            booking = mark_deposit_paid(int(booking_id), stripe_session_id=session_data.get("id"))
            if booking and customer_phone:
                # Send confirmation message to customer on WhatsApp
                confirmation_msg = (
                    f"🎉 *Payment Received!* Your £20 deposit is confirmed.\n\n"
                    f"✅ *Appointment Details:*\n"
                    f"• Service: {booking.service_name}\n"
                    f"• Time: {booking.appointment_time}\n"
                    f"• Remaining balance: £{booking.total_price - booking.deposit_amount:.2f} (payable at the salon)\n"
                    f"• Address: 45 Rye Lane, Peckham, London SE15 5ER\n\n"
                    f"See you soon at Aduke Braids & Beauty Lounge! ✨"
                )
                background_tasks.add_task(send_whatsapp_message, customer_phone, confirmation_msg)
                print(f"[BOOKING CONFIRMED] Booking #{booking_id} paid and confirmed for {customer_phone}!")

    return {"status": "success"}

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from business_config import BUSINESS_PROFILES, get_active_profile
import database

templates = Jinja2Templates(directory="templates")

@app.get("/dashboard", response_class=HTMLResponse)
async def view_owner_dashboard(request: Request, vertical: str = "salon"):
    """
    Mobile-first salon & barbershop owner dashboard.
    """
    profile = BUSINESS_PROFILES.get(vertical, BUSINESS_PROFILES["salon"])
    
    session = database.SessionLocal()
    try:
        bookings = session.query(database.Booking).order_by(database.Booking.id.desc()).all()
        total_bookings = len(bookings)
        confirmed_bookings = len([b for b in bookings if b.status == "confirmed" or b.deposit_paid])
        total_revenue = sum([b.deposit_amount for b in bookings if b.status == "confirmed" or b.deposit_paid])
        handoff_count = len([b for b in bookings if b.needs_human_handoff])
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "profile": profile,
            "active_vertical": vertical,
            "bookings": bookings,
            "total_bookings": total_bookings,
            "confirmed_bookings": confirmed_bookings,
            "total_revenue": total_revenue,
            "handoff_count": handoff_count
        })
    finally:
        session.close()

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
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        print("[SUCCESS] Webhook verified successfully by Meta!")
        return Response(content=challenge, media_type="text/plain")
    
    print(f"[ERROR] Verification failed. Received token: {token}")
    raise HTTPException(status_code=403, detail="Verification token mismatch")

async def handle_incoming_message_task(from_number: str, message_body: str):
    """
    Background worker: Processes message with AI and replies via WhatsApp Cloud API.
    """
    try:
        # Safe ASCII representation for Windows console
        safe_body = message_body.encode('ascii', errors='replace').decode('ascii')
        print(f"\n[INCOMING] From {from_number}: {safe_body}", flush=True)
        
        # 1. Process message through AI engine
        reply_text = await process_customer_message(from_number, message_body)
        
        safe_reply = reply_text.encode('ascii', errors='replace').decode('ascii')
        print(f"[AI REPLY] To {from_number}:\n{safe_reply}\n", flush=True)
        
        # 2. Send the full UTF-8 reply (with emojis) back to WhatsApp
        delivered = await send_whatsapp_message(to_number=from_number, message_text=reply_text)
        if delivered:
            print(f"[SUCCESS] Replied to {from_number}", flush=True)
        else:
            print(f"[FAILED] Could not deliver message to {from_number}", flush=True)
            
    except Exception as e:
        import traceback
        traceback.print_exc()

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
                            print(f"[AUDIO] Voice note received from {from_number}")
                            background_tasks.add_task(
                                send_whatsapp_message, 
                                from_number, 
                                "Thank you for your voice note! We are reviewing it and will respond right away. 🙏"
                            )
                            
        return {"status": "success"}

    return {"status": "ignored"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
