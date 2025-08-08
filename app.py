from flask import Flask, request, Response
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)

# --- Firebase setup ---
try:
    firebase_json = os.environ.get("firebase-key.json")  # Get from Render env vars
    if firebase_json:
        cred_dict = json.loads(firebase_json)  # Convert JSON string to dict
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ Firebase initialized successfully.")
    else:
        db = None
        print("❌ Environment variable 'firebase-key.json' is not set.")
except Exception as e:
    db = None
    print(f"❌ Firebase initialization failed: {e}")

# --- ROUTES ---

@app.route("/")
def hello():
    return "The DIGI9 IVR Brain is running!"

@app.route("/ticket_status/<ticket_id>")
def get_ticket_status(ticket_id):
    if not db:
        return "Firebase not initialized properly."
    try:
        ticket_ref = db.collection('tickets').document(ticket_id)
        ticket = ticket_ref.get()
        if ticket.exists:
            status = ticket.to_dict()['status']
            return f"Status for ticket {ticket_id}: {status}"
        else:
            return f"Ticket {ticket_id} not found."
    except Exception as e:
        print(f"🔥 Error in ticket_status: {e}")
        return "Sorry, an error occurred while fetching the ticket status."

@app.route("/twilio_call_handler", methods=["POST"])
def twilio_call_handler():
    try:
        response = VoiceResponse()

        # Step 1: Welcome message
        response.play("https://cdn.jsdelivr.net/gh/kirtivardhan80/digi9-audio-assets@main/01_welcome_v2.wav")

        # Step 2: Main menu
        gather = Gather(num_digits=1, action="/handle_main_menu", method="POST")
        gather.play("https://cdn.jsdelivr.net/gh/kirtivardhan80/digi9-audio-assets@main/02_main_menu_v3.wav")
        response.append(gather)
        response.redirect("/twilio_call_handler")

        return Response(str(response), mimetype="text/xml")
    except Exception as e:
        print(f"🔥 Error in /twilio_call_handler: {e}")
        fallback = VoiceResponse()
        fallback.say("Sorry, an error occurred.")
        return Response(str(fallback), mimetype="text/xml")

@app.route("/handle_main_menu", methods=["POST"])
def handle_main_menu():
    try:
        digit = request.values.get("Digits")
        response = VoiceResponse()

        if digit == "1":
            response.play("https://cdn.jsdelivr.net/gh/kirtivardhan80/digi9-audio-assets@main/04_sales_transfer.wav")
            response.say("Transferring to sales. Goodbye.")
            response.hangup()
        elif digit == "2":
            gather = Gather(num_digits=1, action="/handle_support_menu", method="POST")
            gather.play("https://cdn.jsdelivr.net/gh/kirtivardhan80/digi9-audio-assets@main/05_support_menu.wav")
            response.append(gather)
            response.redirect("/twilio_call_handler")
        elif digit == "3":
            response.play("https://cdn.jsdelivr.net/gh/kirtivardhan80/digi9-audio-assets@main/06_hr_transfer.wav")
            response.say("Transferring to HR. Goodbye.")
            response.hangup()
        elif digit == "4":
            response.play("https://cdn.jsdelivr.net/gh/kirtivardhan80/digi9-audio-assets@main/07_office_info.wav")
            response.say("Thank you for calling. Goodbye.")
            response.hangup()
        else:
            response.play("https://cdn.jsdelivr.net/gh/kirtivardhan80/digi9-audio-assets@main/03_invalid_input.wav")
            response.redirect("/twilio_call_handler")

        return Response(str(response), mimetype="text/xml")
    except Exception as e:
        print(f"🔥 Error in /handle_main_menu: {e}")
        fallback = VoiceResponse()
        fallback.say("An error occurred in the main menu. Goodbye.")
        fallback.hangup()
        return Response(str(fallback), mimetype="text/xml")

@app.route("/handle_support_menu", methods=["POST"])
def handle_support_menu():
    try:
        digit = request.values.get("Digits")
        response = VoiceResponse()

        if digit == "1":
            response.play("https://cdn.jsdelivr.net/gh/kirtivardhan80/digi9-audio-assets@main/08_log_new_ticket.wav")
            response.say("A new support ticket has been logged. Goodbye.")
            response.hangup()
        elif digit == "2":
            gather = Gather(input="speech dtmf", timeout=5, num_digits=6, action="/handle_ticket_id", method="POST")
            gather.say("Please enter or say your 6-digit ticket ID after the beep.", voice="Polly.Amy", language="en-GB")
            response.append(gather)
            response.say("We didn't receive your input. Goodbye!", voice="Polly.Amy", language="en-GB")
            response.hangup()
        else:
            response.play("https://cdn.jsdelivr.net/gh/kirtivardhan80/digi9-audio-assets@main/03_invalid_input.wav")
            response.redirect("/twilio_call_handler")

        return Response(str(response), mimetype="text/xml")
    except Exception as e:
        print(f"🔥 Error in /handle_support_menu: {e}")
        fallback = VoiceResponse()
        fallback.say("An error occurred in the support menu. Goodbye.")
        fallback.hangup()
        return Response(str(fallback), mimetype="text/xml")

@app.route("/handle_ticket_id", methods=["POST"])
def handle_ticket_id():
    try:
        response = VoiceResponse()
        ticket_id = request.values.get("SpeechResult") or request.values.get("Digits")

        if not ticket_id:
            response.say("No input detected. Returning to the main menu.", voice="Polly.Amy", language="en-GB")
            response.redirect("/twilio_call_handler")
            return Response(str(response), mimetype="text/xml")

        ticket_ref = db.collection('tickets').document(ticket_id)
        ticket = ticket_ref.get()

        if ticket.exists:
            status = ticket.to_dict()['status']
            tts_text = f"The status for your ticket number {ticket_id} is: {status}"
            response.say(tts_text, voice="Polly.Amy", language="en-GB")
        else:
            response.play("https://cdn.jsdelivr.net/gh/kirtivardhan80/digi9-audio-assets@main/03_invalid_input.wav")

        response.say("Thank you for calling DIGI9. Goodbye!", voice="Polly.Amy", language="en-GB")
        response.hangup()

        return Response(str(response), mimetype="text/xml")
    except Exception as e:
        print(f"🔥 Error in /handle_ticket_id: {e}")
        fallback = VoiceResponse()
        fallback.say("Sorry, an error occurred while checking your ticket.")
        fallback.hangup()
        return Response(str(fallback), mimetype="text/xml")

if __name__ == '__main__':
    # For Render, bind to host 0.0.0.0 and port from environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
