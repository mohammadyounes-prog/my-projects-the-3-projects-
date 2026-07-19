from __future__ import annotations
import os
import json
import urllib.request
import urllib.error


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def call_gemini(prompt: str, timeout: int = 20) -> str:
    if not GOOGLE_API_KEY or not GOOGLE_API_KEY.strip():
        raise RuntimeError("GOOGLE_API_KEY is missing or empty. Set it in backend/.env")
    url = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1200}
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            obj = json.loads(resp.read().decode("utf-8"))
            candidates = obj.get("candidates", [])
            if not candidates:
                return ""
            parts = candidates[0].get("content", {}).get("parts", [])
            texts = [p.get("text", "") for p in parts if isinstance(p, dict)]
            return "\n".join([t for t in texts if t]).strip()
    except urllib.error.HTTPError as e:
        try:
            err = e.read().decode("utf-8")
        except Exception:
            err = str(e)
        raise RuntimeError(f"Gemini HTTPError: {e.code} {err}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Gemini URLError: {e}")


def call_gemini_with_model(prompt: str, model: str, timeout: int = 20) -> str:
    os.environ["GEMINI_MODEL"] = model
    return call_gemini(prompt, timeout=timeout)

