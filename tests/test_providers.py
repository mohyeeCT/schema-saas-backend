import pytest

from utils.providers import DEFAULT_MODELS, resolve_model


def test_resolve_model_uses_saved_override():
    assert resolve_model("Claude", "claude-sonnet-4-6") == "claude-sonnet-4-6"


def test_resolve_model_uses_default_when_blank():
    assert resolve_model("Claude", "") == DEFAULT_MODELS["Claude"]


def test_unknown_provider_rejected():
    with pytest.raises(ValueError, match="Unknown provider"):
        resolve_model("UnknownAI", "")
