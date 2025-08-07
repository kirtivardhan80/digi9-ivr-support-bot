#!/usr/bin/env python
# coding: utf-8

# make_test_call.py
# This script places a test call using Twilio's API.

import os
from twilio.rest import Client

# -----------------------------------------
# 🔐 Load sensitive data from environment variables
# -----------------------------------------

# ✅ Twilio Account SID
# 👉 Get this from your [Twilio Console → https://console.twilio.com/]
account_sid = os.getenv("TWILIO_ACCOUNT_SID")

# ✅ Twilio Auth Token
# 👉 Also from your Twilio Console (same place as above)
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

# ✅ Your verified phone number
# 👉 This should be a phone number YOU own and have verified in Twilio
# 👉 Format: +[country code][number], e.g., +911234567890
my_phone_number = os.getenv("MY_PHONE_NUMBER")

# ✅ Your Twilio phone number
# 👉 Found in your Twilio Console under "Phone Numbers"
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")

# ✅ Public URL of your Flask app's webhook
# 👉 If you're running locally, use ngrok and paste the full webhook URL here.
# 👉 Example: https://xxxx.ngrok-free.app/twilio_call_handler
webhook_url = os.getenv("WEBHOOK_URL")

# -----------------------------------------
# ☎️ Initiate the call
# -----------------------------------------

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
