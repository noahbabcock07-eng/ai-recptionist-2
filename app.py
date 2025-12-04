import os
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI

app = Flask(__name__)

# OpenAI client uses your OPENAI_API_KEY env var
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an AI receptionist for a small local business.
Greet callers politely, ask one question at a time,
and keep answers short and clear. If someone wants to
book an appointment, ask for their name, phone number,
date and time, and the service they want.
If you are not sure about something, say that a human
will call them back to confirm.
"""


def get_ai_reply(user_text: str) -> str:
    """
    Send caller text to OpenAI and get a short reply.
    """
    if not user_text:
        return "I did not hear anything. Can you please repeat that"

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            max_tokens=120,
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        # Fail safe so calls do not crash if OpenAI has an issue
        return (
            "Sorry, I am having trouble right now. "
            "Please call back in a few minutes."
        )


@app.route("/", methods=["GET"])
def index():
    return "AI receptionist is running"


@app.route("/voice", methods=["POST"])
def voice():
    """
    First webhook Twilio hits when the call starts.
    We greet the caller and use Gather with speech input.
    """
    resp = VoiceResponse()

    gather = Gather(
        input="speech",
        action="/handle_speech",  # Twilio will POST here with SpeechResult
        method="POST",
        language="en-US",
        speech_timeout="auto",
    )
    gather.say("Hi, this is the receptionist. How can I help you today")
    resp.append(gather)

    # If no speech was captured, Twilio will fall through to this
    resp.say("I did not hear anything. Goodbye.")
    return Response(str(resp), mimetype="application/xml")


@app.route("/handle_speech", methods=["POST"])
def handle_speech():
    """
    Twilio sends the transcribed speech here as 'SpeechResult'.
    We send it to OpenAI, speak the answer,
    then start another Gather so the conversation can continue.
    """
    speech_result = request.values.get("SpeechResult", "")

    resp = VoiceResponse()

    if not speech_result:
        resp.say("I did not hear anything. Goodbye.")
        return Response(str(resp), mimetype="application/xml")

    ai_text = get_ai_reply(speech_result)

    # Speak AI reply
    resp.say(ai_text)

    # Start another turn of the conversation
    gather = Gather(
        input="speech",
        action="/handle_speech",
        method="POST",
        language="en-US",
        speech_timeout="auto",
    )
    gather.say("You can say something else, or say goodbye to end the call.")
    resp.append(gather)

    return Response(str(resp), mimetype="application/xml")


if __name__ == "__main__":
    # For local testing; on Render, gunicorn runs app directly
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
