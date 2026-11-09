import os
import requests

GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v22.0")

def create_reply(message_text):
    """Simple starter rules. Customize these replies for your business."""
    text = (message_text or "").lower().strip()

    if any(word in text for word in ("hello", "hi", "salam", "assalam")):
        return "Hello! 👋 Thanks for contacting us. How can we help you today?"
    if "price" in text or "pricing" in text or "rate" in text:
        return "Thanks for asking about pricing. Please tell us which product or service you need."
    if "order" in text or "delivery" in text:
        return "I'd be happy to help with your order. Please share your order number."
    if "help" in text or "support" in text:
        return "Of course! Please describe what you need help with, and our team will assist you."
    if "thank" in text or "shukriya" in text:
        return "You're welcome! 😊 Is there anything else I can help you with?"
    return (
        "Thanks for your message! We've received it. "
        "Please share a little more detail so we can help you."
    )

def send_whatsapp_message(to, body):
    token = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    if not token or not phone_number_id:
        raise RuntimeError("Set WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID.")
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": body},
    }
    response = requests.post(url, headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    return response.json()
