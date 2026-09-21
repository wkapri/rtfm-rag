import pytest

from ragapp.config import settings
from ragapp.llm.factory import create_llm_client
from ragapp.llm.providers.anthropic import AnthropicProvider
from ragapp.llm.providers.ollama import OllamaProvider
from ragapp.llm.providers.openai_compat import OpenAICompatProvider


def test_defaults_to_ollama():
    client = create_llm_client()
    assert isinstance(client, OllamaProvider)


def test_explicit_ollama():
    assert isinstance(create_llm_client("ollama"), OllamaProvider)


def test_openai_requires_api_key(monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", None)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        create_llm_client("openai")


def test_openai_with_api_key(monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", "sk-test")
    client = create_llm_client("openai")
    assert isinstance(client, OpenAICompatProvider)


def test_anthropic_requires_api_key(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", None)
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        create_llm_client("anthropic")


def test_anthropic_with_api_key(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "sk-ant-test")
    client = create_llm_client("anthropic")
    assert isinstance(client, AnthropicProvider)


def test_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
        create_llm_client("carrier-pigeon")
