import os
import json
import urllib.request
import urllib.error


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def call_openai_chat(prompt: str, model: str | None = None, timeout: int = 20, api_key: str | None = None) -> str:
    """Call OpenAI Chat Completions API with a simple prompt and return text.

    Uses provided api_key or environment OPENAI_API_KEY. Keeps dependencies minimal by using urllib.
    """
    key = api_key or OPENAI_API_KEY
    if not key or not key.strip():
        raise RuntimeError("OPENAI_API_KEY is missing or empty. Set it in backend/.env or provide it.")

    # Use a sensible default model if none is provided. We respect the existing env if present.
    mdl = model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    body = {
        "model": mdl,
        "messages": [
            {"role": "system", "content": (
                "You are an expert question generator. Output ONLY in the exact format requested. "
                "Do not include any explanations or JSON."
            )},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 1200,
    }

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_body = resp.read().decode("utf-8")
            obj = json.loads(resp_body)
            # Standard shape: choices[0].message.content
            return obj.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    except urllib.error.HTTPError as e:
        try:
            err = e.read().decode("utf-8")
        except Exception:
            err = str(e)
        raise RuntimeError(f"OpenAI HTTPError: {e.code} {err}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"OpenAI URLError: {e}")
