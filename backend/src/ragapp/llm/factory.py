from ragapp.config import settings
from ragapp.llm.base import LLMProvider
from ragapp.llm.providers.anthropic import AnthropicProvider
from ragapp.llm.providers.ollama import OllamaProvider
from ragapp.llm.providers.openai_compat import OpenAICompatProvider


def create_llm_client(provider: str | None = None) -> LLMProvider:
    """Build the configured chat LLMProvider. Defaults to settings.llm_provider
    ("ollama" unless overridden), so existing callers that don't care which
    provider they get keep working unchanged.
    """
    provider = provider or settings.llm_provider

    if provider == "ollama":
        return OllamaProvider()

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        return OpenAICompatProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_chat_model,
            base_url=settings.openai_base_url,
        )

    if provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic")
        return AnthropicProvider(api_key=settings.anthropic_api_key, model=settings.anthropic_chat_model)

    raise ValueError(f"Unknown LLM_PROVIDER: {provider!r} (expected ollama, openai, or anthropic)")
