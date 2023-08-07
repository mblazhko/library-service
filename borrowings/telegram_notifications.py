import requests
from django.conf import settings


def send_telegram_notification(message):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": message,
    }
    response = requests.post(url, json=data)
    return response.json()
