"""LLM factory from settings."""

from langchain_core.language_models import BaseChatModel

from research_gap_agent.config import LLMProvider, RuntimeConfig, Settings


def get_llm(settings: Settings | RuntimeConfig) -> BaseChatModel:
    """Return the configured chat model."""
    if settings.llm_provider == LLMProvider.OPENAI:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            api_key=settings.openai_api_key,
        )
    if settings.llm_provider == LLMProvider.ANTHROPIC:
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            api_key=settings.anthropic_api_key,
        )
    raise ValueError(f"Unknown provider: {settings.llm_provider}")
