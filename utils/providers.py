DEFAULT_MODELS = {
    "Claude": "claude-sonnet-5",
    "OpenAI": "gpt-4.1",
    "Gemini (free)": "gemini-2.0-flash",
    "Mistral (free tier)": "mistral-small-latest",
    "Groq (free tier)": "llama-3.3-70b-versatile",
}


def resolve_model(provider: str, model: str | None) -> str:
    if provider not in DEFAULT_MODELS:
        raise ValueError(f"Unknown provider: {provider}")
    return model or DEFAULT_MODELS[provider]


def generate_schema_text(
    provider: str,
    api_key: str,
    prompt: str,
    model: str | None = None,
) -> str:
    resolved_model = resolve_model(provider, model)
    if provider == "Claude":
        return _call_claude(api_key, prompt, resolved_model)
    raise ValueError(f"Provider not yet implemented for schema generator: {provider}")


def _call_claude(api_key: str, prompt: str, model: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=8192,
        system=prompt,
        messages=[{
            "role": "user",
            "content": "Generate the requested schema JSON-LD now.",
        }],
    )
    return "\n".join(
        block.text for block in response.content if getattr(block, "type", "") == "text"
    )
