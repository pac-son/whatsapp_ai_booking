import os
from typing import Dict, List
import google.generativeai as genai
from prompt import SALON_SYSTEM_PROMPT

# Track user conversation history in memory for MVP (keyed by phone number)
# Format: { "+234...": [ {"role": "user", "parts": [...]}, {"role": "model", "parts": [...]} ] }
conversation_sessions: Dict[str, any] = {}

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_or_create_chat(phone_number: str):
    """
    Returns an existing chat session or creates a new one with the salon system instructions.
    """
    if phone_number not in conversation_sessions:
        # Initialize Gemini 1.5 Flash model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SALON_SYSTEM_PROMPT,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 500,
            }
        )
        conversation_sessions[phone_number] = model.start_chat(history=[])
    
    return conversation_sessions[phone_number]

async def process_customer_message(phone_number: str, user_text: str) -> str:
    """
    Processes an incoming message through the AI model and returns the response.
    """
    try:
        # If API key is not yet set, provide a realistic mock response so testing works immediately
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            # Normalize multiple spaces and lowercase for reliable matching
            text_clean = " ".join(user_text.lower().split())

            # Detect human handoff request
            handoff_triggers = [
                "speak to human", "speak with human", "speak to someone", "talk to human",
                "speak with owner", "speak to owner", "call owner", "call aduke", "talk to aduke",
                "complaint", "speak to manager", "talk to manager", "human agent", "talk to a person", "human",
                "owner", "aduke"
            ]
            if any(trigger in text_clean for trigger in handoff_triggers):
                from database import trigger_human_handoff
                trigger_human_handoff(phone_number, reason=user_text)
                
                # Send notification alert to the owner's WhatsApp
                owner_phone = os.getenv("OWNER_PHONE_NUMBER", "2348067421594")
                if owner_phone:
                    from whatsapp_client import send_whatsapp_message
                    alert_text = (
                        f"🚨 *SALON OWNER ALERT: HUMAN HANDOFF NEEDED*\n\n"
                        f"📱 Customer: +{phone_number}\n"
                        f"💬 Message: \"{user_text}\"\n\n"
                        f"The customer requested to speak with you directly. You can now reply to them in WhatsApp!"
                    )
                    await send_whatsapp_message(to_number=owner_phone, message_text=alert_text)

                return (
                    "No wahala at all! I don notify Aduke, our salon owner. 🙋🏾‍♀️\n\n"
                    "She go check this chat and message you directly shortly. Thank you for your patience! 🙏"
                )

            # Barbershop intent detection
            barber_keywords = ["fade", "haircut", "beard", "line up", "shape up", "trim", "barber", "shave"]
            if any(k in text_clean for k in barber_keywords):
                if any(w in text_clean for w in ["book", "slot", "available", "friday", "saturday", "tomorrow", "today"]):
                    from database import create_booking_record
                    from stripe_service import create_deposit_checkout_session
                    
                    booking = create_booking_record(
                        phone=phone_number,
                        service="Skin Fade & Line Up",
                        appt_time="Friday 3:00 PM",
                        total_price=30.0,
                        deposit=10.0
                    )
                    pay_link = create_deposit_checkout_session(
                        booking_id=booking.id,
                        service_name=booking.service_name,
                        deposit_amount=booking.deposit_amount,
                        customer_phone=phone_number
                    )
                    return (
                        f"Sharp! We got Friday at 3:00 PM open at Krowns & Fades Afro Barbershop! 👑💈\n\n"
                        f"📋 *Booking Summary:*\n"
                        f"• Service: Skin Fade & Line Up (£30)\n"
                        f"• Time: Friday @ 3:00 PM\n"
                        f"• Deposit required: £10\n\n"
                        f"Lock in your chair with your £10 deposit here:\n{pay_link}\n\n"
                        f"Once paid, your slot is 100% reserved. Clean cuts only, my bro! ✂️"
                    )
                else:
                    return (
                        "Bless up king! Welcome to Krowns & Fades Afro Barbershop! 👑💈\n\n"
                        "Here na our popular cut prices:\n"
                        "• Skin Fade & Line Up: £30 (45 mins)\n"
                        "• Haircut & Shape Up: £25 (30 mins)\n"
                        "• Beard Sculpt & Hot Towel: £20\n"
                        "• The VIP Full Service (Cut + Beard + Facial): £55\n\n"
                        "Which day and time you go like come through for your cut?"
                    )

            if any(w in text_lower for w in ["how far", "abeg", "wetin", "dey", "na"]):
                return (
                    "How far! Welcome to Aduke Braids & Beauty Lounge! 😊 "
                    "I be Timi, your booking assistant. Wetin you go like do to your hair today? "
                    "We dey do Knotless Braids, Box Braids, Boho Braids, and Stitch Cornrows!"
                )
            elif "price" in text_lower or "how much" in text_lower:
                return (
                    "Hello! Our popular services include:\n"
                    "• Medium Knotless Braids: £120 (approx 4 hrs)\n"
                    "• Small Knotless Braids: £160\n"
                    "• Traditional Box Braids: £100\n"
                    "• Stitch Braids: from £50\n\n"
                    "Which style would you like to book for?"
                )
            elif any(w in text_lower for w in ["book", "slot", "available", "friday", "saturday", "tomorrow", "today"]):
                from database import create_booking_record
                from stripe_service import create_deposit_checkout_session
                
                booking = create_booking_record(
                    phone=phone_number,
                    service="Medium Knotless Braids",
                    appt_time="Friday 2:00 PM",
                    total_price=120.0,
                    deposit=20.0
                )
                pay_link = create_deposit_checkout_session(
                    booking_id=booking.id,
                    service_name=booking.service_name,
                    deposit_amount=booking.deposit_amount,
                    customer_phone=phone_number
                )
                return (
                    f"We got Friday at 2:00 PM open for you! 🎉\n\n"
                    f"📋 *Booking Summary:*\n"
                    f"• Service: Medium Knotless Braids (£120)\n"
                    f"• Time: Friday @ 2:00 PM\n"
                    f"• Deposit required: £20\n\n"
                    f"To lock down your seat, please pay the £20 deposit here:\n{pay_link}\n\n"
                    f"Once paid, your appointment is 100% confirmed! No wahala!"
                )
            else:
                return (
                    "Hello and welcome to Aduke Braids & Beauty Lounge! ✨ "
                    "I am Timi, the automated salon assistant. How can I help you today? "
                    "You can ask about our styles, prices, or book an appointment."
                )

        # Call Gemini AI
        chat = get_or_create_chat(phone_number)
        response = chat.send_message(user_text)
        return response.text.strip()

    except Exception as e:
        print(f"[ERROR] Error processing message with AI: {e}")
        return "Thank you for reaching out to Aduke Braids Lounge! Our team has received your message and will reply shortly. 🙏"
