from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_anon_key: str = ""

    # AI Providers
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Server
    cors_origins: str = "http://localhost:3000"
    log_level: str = "INFO"
    environment: str = "development"

    model_config = {"env_file": ".env"}


settings = Settings()
