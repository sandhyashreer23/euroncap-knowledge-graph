"""Quick Gemini check:  python check_gemini.py

1. Shows which version of llm.py you are running.
2. Lists the Gemini models your key can use.
3. Sends one tiny test request to each candidate model and reports OK / error.
"""
import os

from kg import llm
from kg.config import GEMINI_MODEL

print("llm.py has fallback support:", hasattr(llm, "FALLBACK_MODEL"))
print("Key found:", bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")))

client = llm._get_client()

print("\nModels your key can use for text generation:")
available = []
for m in client.models.list():
    if "generateContent" in (getattr(m, "supported_actions", None) or []):
        name = m.name.replace("models/", "")
        available.append(name)
        print("  ", name)

candidates = [GEMINI_MODEL, os.getenv("GEMINI_FALLBACK_MODEL", "")]
candidates += [n for n in available if "flash" in n][:4]
seen = set()
print("\nTest requests:")
for name in candidates:
    if not name or name in seen:
        continue
    seen.add(name)
    try:
        r = client.models.generate_content(model=name, contents="Reply with the word OK.")
        print(f"   OK     {name}  -> {(r.text or '').strip()[:20]}")
    except Exception as err:
        print(f"   ERROR  {name}  -> {str(err)[:90]}")

print("\nPut a model marked OK into .env as GEMINI_MODEL (and another OK one as GEMINI_FALLBACK_MODEL).")