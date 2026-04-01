"""
Unified LLM client supporting NVIDIA NIM, Ollama (local), and Groq (cloud).
"""

import json
from backend.config import settings


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 4096) -> str:
    """Route to the configured LLM provider."""
    if settings.LLM_PROVIDER == "nvidia":
        return _call_nvidia(system_prompt, user_prompt, temperature, max_tokens)
    elif settings.LLM_PROVIDER == "groq":
        return _call_groq(system_prompt, user_prompt, temperature, max_tokens)
    else:
        return _call_ollama(system_prompt, user_prompt, temperature, max_tokens)


def _call_nvidia(system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
    """Call Llama via NVIDIA NIM API (OpenAI-compatible)."""
    from openai import OpenAI

    client = OpenAI(
        base_url=settings.NVIDIA_BASE_URL,
        api_key=settings.NVIDIA_API_KEY,
    )
    response = client.chat.completions.create(
        model=settings.NVIDIA_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def _call_ollama(system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
    """Call local Llama via Ollama."""
    import ollama

    response = ollama.chat(
        model=settings.OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        options={
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    )
    return response["message"]["content"]


def _call_groq(system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
    """Call Llama via Groq cloud API."""
    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def call_llm_json(system_prompt: str, user_prompt: str, temperature: float = 0.4) -> dict:
    """Call LLM and parse response as JSON."""
    enhanced_system = system_prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown fences, no explanation outside the JSON."
    raw = call_llm(enhanced_system, user_prompt, temperature=temperature)

    # Clean common issues
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try to find JSON in the response
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(raw[start:end])
            except json.JSONDecodeError:
                pass
        return {"raw_response": raw, "parse_error": True}