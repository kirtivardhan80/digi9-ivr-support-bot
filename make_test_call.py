#!/usr/bin/env python
# coding: utf-8

# make_test_call.py

import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load .env file
load_dotenv()

# --- Load credentials from environment ---
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
my_phone_number = os.getenv("MY_PHONE_NUMBER")
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
webhook_url = os.getenv("WEBHOOK_URL")

# --- Make test call ---
try:
    print("📞 Attempting to make a test call via the Twilio API...")
    client = Client(account_sid, auth_token)

    call = client.calls.create(
        url=webhook_url,
        to=my_phone_number,
        from_=twilio_phone_number
    )

    print("✅ Success! The call is being initiated.")
    print(f"📄 Call SID (unique ID): {call.sid}")

except Exception as e:
    print(f"❌ An error occurred: {e}")
