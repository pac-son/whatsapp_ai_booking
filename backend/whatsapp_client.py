import os
import httpx
from typing import Optional
from dotenv import load_dotenv

GRAPH_API_VERSION = "v21.0"

async def send_whatsapp_message(to_number: str, message_text: str) -> bool:
    """
    Sends a text message to a user via the WhatsApp Cloud API.
    Always reloads .env so token updates take effect immediately without restarting.
    """
    load_dotenv(override=True)
    
    token = os.getenv("WHATSAPP_API_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID", "1361885143683747")
    
    if not token:
        print("[WARNING] WHATSAPP_API_TOKEN is not set. Cannot send message.")
        return False

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message_text
        }
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code in [200, 201]:
                print(f"[SUCCESS] Message delivered to {to_number}")
                return True
            else:
                print(f"[ERROR] Failed to send message: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"[EXCEPTION] Error sending WhatsApp message: {e}")
            return False
