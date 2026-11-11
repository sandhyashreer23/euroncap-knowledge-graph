"""Thin wrapper around Gemini so the rest of the code never touches the SDK."""
import json
import os
import time

from kg.config import ENV_FILE, GEMINI_MODEL

_client = None


def _get_client():
    global _client
    if _client is None:
        key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not key:
            raise SystemExit(
                f"\nNo GEMINI_API_KEY found.\n"
                f"  Expected file: {ENV_FILE}  (exists: {ENV_FILE.exists()})\n"
                f"  It must contain one line:  GEMINI_API_KEY=your-key  (no spaces, no quotes)\n"
            )
        from google import genai  # pip install google-genai
        _client = genai.Client(api_key=key)
    return _client


FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "")


def generate(prompt: str, as_json: bool = False, retries: int = 6) -> str:
    """Call Gemini with retry/backoff (5s, 10s, 20s, 40s, 60s...).
    If GEMINI_FALLBACK_MODEL is set, switches to it after 2 failed attempts
    (useful when the main model returns 503 'high demand')."""
    cfg = {"temperature": 0}
    if as_json:
        cfg["response_mime_type"] = "application/json"
    client = _get_client()  # fails fast with a clear message if the key is missing
    model = GEMINI_MODEL
    for attempt in range(retries):
        try:
            resp = client.models.generate_content(model=model, contents=prompt, config=cfg)
            return resp.text or ""
        except Exception as err:  # 503 overload, 429 rate limit, transient errors
            if attempt == retries - 1:
                raise
            if FALLBACK_MODEL and attempt >= 1 and model != FALLBACK_MODEL:
                model = FALLBACK_MODEL
                print(f"  Switching to fallback model: {model}")
            wait = min(5 * 2 ** attempt, 60)
            print(f"  Gemini busy ({str(err)[:60]}...); retrying in {wait}s")
            time.sleep(wait)
    return ""


def generate_json(prompt: str) -> dict:
    """Same as generate(), but parsed. Returns {} if the model returns junk."""
    text = generate(prompt, as_json=True)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}