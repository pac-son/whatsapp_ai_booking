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
            # Fallback mock engine demonstrating Pidgin & English awareness
            text_lower = user_text.lower()
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
            elif "book" in text_lower or "slot" in text_lower or "available" in text_lower:
                return (
                    "We have slots open this week from Wednesday to Saturday between 9:00 AM and 7:00 PM! "
                    "Which day and time works best for you? (Please note a £20 deposit is required to secure your booking)."
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
