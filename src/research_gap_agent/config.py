"""Application settings and config. YAML is mandatory; required keys must be present."""

from enum import Enum
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DepthPreset(str, Enum):
    """Search depth presets."""

    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class DepthPresetConfig(BaseModel):
    """One depth preset: search limits and cluster range."""

    min_papers: int
    max_papers: int
    max_search_iterations: int
    min_clusters: int = Field(ge=1, le=20, description="Min number of topic clusters")
    max_clusters: int = Field(ge=1, le=20, description="Max number of topic clusters")

    @model_validator(mode="after")
    def clusters_order(self) -> "DepthPresetConfig":
        if self.min_clusters > self.max_clusters:
            raise ValueError("min_clusters must be <= max_clusters")
        return self


class DepthPresetsConfig(BaseModel):
    """All three depth presets; keys must be quick, standard, deep."""

    quick: DepthPresetConfig
    standard: DepthPresetConfig
    deep: DepthPresetConfig


class LLMConfig(BaseModel):
    """LLM section from config.yaml. All fields required."""

    provider: Literal["openai", "anthropic"]
    model: str
    temperature: float = Field(ge=0.0, le=2.0)
    hypothesis_temperature: float = Field(ge=0.0, le=2.0)


class AppConfig(BaseModel):
    """YAML config file structure. llm, literature_apis, depth_presets required."""

    llm: LLMConfig
    literature_apis: list[str]
    depth_presets: DepthPresetsConfig
    relevance_threshold: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="LLM relevance score 0–1; papers below this are dropped. Used for all depths.",
    )


def load_config(path: Path | str | None = None) -> AppConfig:
    """Load and validate AppConfig from YAML. Raises if file missing or required key missing."""
    if path is None:
        path = Path("config.yaml")
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file required but not found: {path}")
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    if not data:
        raise ValueError(f"Config file is empty: {path}")
    return AppConfig.model_validate(data)


class Settings(BaseSettings):
    """Env-only settings: API keys. LLM and app config come from YAML."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    semantic_scholar_api_key: str | None = Field(default=None, description="Semantic Scholar API key")
    openalex_api_key: str | None = Field(default=None, description="OpenAlex API key")


class RuntimeConfig(BaseModel):
    """Merged config (YAML + env) for building the graph. API keys from Settings only."""

    llm_provider: LLMProvider
    llm_model: str
    llm_temperature: float = Field(ge=0.0, le=2.0)
    hypothesis_temperature: float = Field(ge=0.0, le=2.0)
    literature_apis: list[str]
    depth_presets: dict[str, dict]
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    semantic_scholar_api_key: str | None = None
    openalex_api_key: str | None = None

    class Config:
        extra = "forbid"


def get_runtime_config(
    config_path: Path | str | None = None,
    settings: Settings | None = None,
    *,
    llm_provider_override: LLMProvider | None = None,
) -> RuntimeConfig:
    """Build RuntimeConfig from YAML + env. YAML must exist and include all required keys."""
    settings = settings or Settings()
    app = load_config(path=config_path)
    provider = llm_provider_override or LLMProvider(app.llm.provider)
    depth_presets = {}
    for name, preset in [
        ("quick", app.depth_presets.quick),
        ("standard", app.depth_presets.standard),
        ("deep", app.depth_presets.deep),
    ]:
        d = preset.model_dump()
        d["relevance_threshold"] = app.relevance_threshold
        depth_presets[name] = d
    return RuntimeConfig(
        llm_provider=provider,
        llm_model=app.llm.model,
        llm_temperature=app.llm.temperature,
        hypothesis_temperature=app.llm.hypothesis_temperature,
        literature_apis=app.literature_apis,
        depth_presets=depth_presets,
        openai_api_key=settings.openai_api_key,
        anthropic_api_key=settings.anthropic_api_key,
        semantic_scholar_api_key=settings.semantic_scholar_api_key,
        openalex_api_key=settings.openalex_api_key,
    )
