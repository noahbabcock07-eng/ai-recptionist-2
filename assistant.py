import os
import openai
from datetime import datetime

openai.api_key = os.environ.get("OPENAI_API_KEY")

def parse_intent_from_reply(reply: str) -> dict | None:
    """
    Very simple intent parser.
    Looks for phrases like 'schedule an appointment on <date> at <time>'.
    Returns an action dict if scheduling is requested; otherwise None.
    """
    lower = reply.lower()
    if "schedule" in lower and "appointment" in lower:
        try:
            parts = lower.split("on")[1].strip().split("at")
            date_str = parts[0].strip()
            time_str = parts[1].strip().split()[0]
            datetime.strptime(date_str, "%Y-%m-%d")
            return {
                "type": "create_appointment",
                "date": date_str,
                "time": time_str,
                "title": "Customer appointment",
                "description": "Auto-booked via AI receptionist"
            }
        except Exception:
            return None
    return None

def handle_user_prompt(prompt: str) -> tuple[str, dict | None]:
    """
    Sends the caller's prompt to OpenAI and returns a tuple:
    (reply_to_user, optional_action).
    """
    system_prompt = (
        "You are a friendly female receptionist for a barbershop. "
        "Answer questions succinctly and clearly. "
        "If the user wants to book an appointment, ask for the desired date and time "
        "in YYYY-MM-DD and HH:MM format. "
        "When the date and time are provided, restate the appointment and "
        "indicate that you will schedule it."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        max_tokens=150,
        temperature=0.5,
    )
    ai_reply = completion.choices[0].message["content"].strip()
    action = parse_intent_from_reply(ai_reply)
    return ai_reply, action
