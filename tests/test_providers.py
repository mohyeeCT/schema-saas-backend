import sys
import types

import pytest

from utils.providers import DEFAULT_MODELS, resolve_model
from utils import providers


def test_resolve_model_uses_saved_override():
    assert resolve_model("Claude", "claude-sonnet-4-6") == "claude-sonnet-4-6"


def test_resolve_model_uses_default_when_blank():
    assert resolve_model("Claude", "") == DEFAULT_MODELS["Claude"]


def test_unknown_provider_rejected():
    with pytest.raises(ValueError, match="Unknown provider"):
        resolve_model("UnknownAI", "")


def test_sonnet_5_schema_call_disables_thinking():
    captured = {}

    class FakeMessages:
        def create(self, **kwargs):
            captured.update(kwargs)
            return types.SimpleNamespace(
                content=[types.SimpleNamespace(type="text", text='{"@context":"https://schema.org"}')]
            )

    class FakeAnthropic:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    anthropic_stub = types.ModuleType("anthropic")
    anthropic_stub.Anthropic = FakeAnthropic
    original_anthropic = sys.modules.get("anthropic")
    sys.modules["anthropic"] = anthropic_stub
    try:
        providers._call_claude("key", "prompt", "claude-sonnet-5")
    finally:
        if original_anthropic is None:
            sys.modules.pop("anthropic", None)
        else:
            sys.modules["anthropic"] = original_anthropic

    assert captured["thinking"] == {"type": "disabled"}
    assert captured["max_tokens"] == 8192
