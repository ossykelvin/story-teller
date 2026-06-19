import requests
from core.config import env, DEFAULT_PROVIDER, FALLBACK_PROVIDER, get_model
from core.prompts import SYSTEM_RULES

class AIClientError(Exception):
    pass


def _openrouter_chat(prompt: str, purpose: str, temperature: float = 0.7) -> str:
    api_key = env("OPENROUTER_API_KEY", "")
    if not api_key:
        raise AIClientError("OpenRouter API key is missing. Add OPENROUTER_API_KEY to .env.local.")
    model = get_model("openrouter", purpose) or env("OPENROUTER_WRITING_MODEL", "")
    if not model:
        raise AIClientError(f"OpenRouter model for {purpose} is missing in .env.local.")
    url = env("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8443",
        "X-Title": env("APP_NAME", "Uncle Ossy StoryTeller"),
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_RULES},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=90)
    if r.status_code >= 400:
        raise AIClientError(f"OpenRouter error {r.status_code}: {r.text[:800]}")
    data = r.json()
    return data["choices"][0]["message"]["content"]


def _gemini_chat(prompt: str, purpose: str, temperature: float = 0.7) -> str:
    api_key = env("GEMINI_API_KEY", "")
    if not api_key:
        raise AIClientError("Gemini API key is missing. Add GEMINI_API_KEY to .env.local.")
    model = get_model("gemini", purpose) or env("GEMINI_WRITING_MODEL", "gemini-1.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": SYSTEM_RULES + "\n\n" + prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    r = requests.post(url, json=payload, timeout=90)
    if r.status_code >= 400:
        raise AIClientError(f"Gemini error {r.status_code}: {r.text[:800]}")
    data = r.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as exc:
        raise AIClientError(f"Gemini returned an unexpected response: {data}") from exc


def generate_text(prompt: str, purpose: str = "writing", provider: str | None = None, allow_fallback: bool = True, temperature: float = 0.7) -> str:
    selected = provider or env("DEFAULT_PROVIDER", DEFAULT_PROVIDER)
    fallback = env("FALLBACK_PROVIDER", FALLBACK_PROVIDER)
    errors = []
    for candidate in ([selected, fallback] if allow_fallback and fallback != selected else [selected]):
        try:
            if candidate == "openrouter":
                return _openrouter_chat(prompt, purpose, temperature)
            if candidate == "gemini":
                return _gemini_chat(prompt, purpose, temperature)
            raise AIClientError(f"Unsupported provider: {candidate}")
        except Exception as exc:
            errors.append(f"{candidate}: {exc}")
    raise AIClientError("; ".join(errors))
