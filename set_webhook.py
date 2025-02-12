import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()  # Load .env file

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

if TG_BOT_TOKEN is None:
    exit("Telegram Bot Token is not found in `.env` file")
if len(sys.argv) != 2:
    exit("Usage: python set_webhook.py [Ngrok URL]")


NGROK_URL = sys.argv[1].strip("/")

requests.post(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/setWebhook", params={"url": f"{NGROK_URL}/webhook"})

response = requests.get(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getWebhookInfo")

print(response.json())
