"""Application settings loaded from environment. Never log secret values."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Supabase
    supabase_url: str = ""
    supabase_publishable_key: str = ""
    supabase_secret_key: str = ""
    supabase_db_password: str = ""
    # Legacy aliases (optional)
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    bootstrap_auth_email: str = "phillmhembere@gmail.com"
    bootstrap_auth_password: str = ""

    @property
    def supabase_key_public(self) -> str:
        return self.supabase_publishable_key or self.supabase_anon_key

    @property
    def supabase_key_secret(self) -> str:
        return self.supabase_secret_key or self.supabase_service_role_key

    # AI
    gemini_api_key: str = ""
    groq_api_key: str = ""
    hf_token: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_api_key: str = ""
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_enabled: bool = False  # set OLLAMA_ENABLED=true locally when Ollama is running

    # Scraping
    firecrawl_api_key: str = ""
    scrapingbee_api_key: str = ""
    apify_api_token: str = ""
    tavily_api_key: str = ""

    # Pipeline
    ai_daily_cloud_call_limit: int = 200
    discovery_max_terms: int = 60
    discovery_max_sources: int = 60
    scrape_max_urls: int = 60
    ai_analysis_limit: int = 40
    chroma_persist_dir: str = "./data/chroma"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
