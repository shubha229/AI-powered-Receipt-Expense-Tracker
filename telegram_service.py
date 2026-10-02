import requests
import streamlit as st


BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
CHAT_ID = str(st.secrets["TELEGRAM_CHAT_ID"])


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("ok"):
            return True, data["result"]["message_id"]

        return False, data.get(
            "description",
            "Telegram API request failed"
        )

    except Exception as error:
        return False, str(error)