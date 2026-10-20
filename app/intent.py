from enum import StrEnum, auto
import os
import httpx

class ShiftRequestMessageIntent(StrEnum):
    ACCEPT = auto()
    DECLINE = auto()
    UNKNOWN = auto()


# Configurable via environment variable
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma2:2b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


async def parse_shift_request_message_intent(
    message: str,
) -> ShiftRequestMessageIntent:
    """
    Parse the intent of an inbound caregiver message using a local
    open-weight model (Ollama). Falls back to UNKNOWN on any error
    so the service never crashes.
    """
    prompt = f"""You are classifying a short SMS reply from a caregiver about an open shift.

Reply with EXACTLY one word: ACCEPT, DECLINE, or UNKNOWN.

Examples:
- "yes I can take it" → ACCEPT
- "yeah sure put me down" → ACCEPT
- "nope I'm booked" → DECLINE
- "sorry can't make it" → DECLINE
- "what time does it start?" → UNKNOWN
- "ok" → ACCEPT
- "nah" → DECLINE

Message: "{message.strip()}"
"""

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.0,  # deterministic
                        "num_predict": 10,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            text = data["message"]["content"].strip().upper()

            if "ACCEPT" in text:
                return ShiftRequestMessageIntent.ACCEPT
            if "DECLINE" in text:
                return ShiftRequestMessageIntent.DECLINE
            return ShiftRequestMessageIntent.UNKNOWN

    except Exception:
        # Network error, model not pulled, timeout, etc.
        # Never let the whole service fail because of the model.
        return ShiftRequestMessageIntent.UNKNOWN