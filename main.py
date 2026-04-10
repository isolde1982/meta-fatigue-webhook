from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import os
import json
import logging
import requests

app = FastAPI()

VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "dev_meta_webhook_2026")
TEAMS_WEBHOOK_URL = "https://oneomnicom.webhook.office.com/webhookb2/7e99a2ab-43fd-44bd-a81b-b707e7f83f6e@41eb501a-f671-4ce0-a5bf-b64168c3705f/IncomingWebhook/23707c06590641c0b8e0c177566edead/267fc4fc-be49-4502-a497-890d99112f67/V25mdyTiLV6w_IAP3lKK8hF7trMcRA7bJNLrcoYXwSwFE1"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("meta-fatigue-webhook")


def send_teams_notification(message: str) -> None:
    if not TEAMS_WEBHOOK_URL:
        logger.warning("TEAMS_WEBHOOK_URL is missing; skipping Teams notification.")
        return

    payload = {"text": message}
    response = requests.post(TEAMS_WEBHOOK_URL, json=payload, timeout=30)
    response.raise_for_status()


@app.get("/webhook", response_class=PlainTextResponse)
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN and challenge:
        logger.info("Webhook verified successfully.")
        return challenge

    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    logger.info("Incoming webhook payload: %s", json.dumps(payload))

    send_teams_notification(f"Meta creative fatigue notification received:\n{json.dumps(payload, indent=2)}")

    return {"status": "received"}


@app.get("/")
async def root():
    return {"message": "Meta Creative Fatigue webhook is running"}
