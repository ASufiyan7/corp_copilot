from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices
from typing import Optional

class Settings(BaseSettings):
    # Supabase Settings
    supabase_url: str = Field(validation_alias=AliasChoices("SUPABASE_URL", "VITE_SUPABASE_URL"))
    supabase_anon_key: str = Field(validation_alias=AliasChoices("SUPABASE_ANON_KEY", "VITE_SUPABASE_ANON_KEY"))
    supabase_service_role_key: str = Field(validation_alias="SUPABASE_SERVICE_ROLE_KEY")
    
    # Database Settings
    database_url: str = Field(validation_alias="DATABASE_URL")
    
    # LLM Provider Configuration
    llm_provider: str = Field(default="groq", validation_alias=AliasChoices("LLM_PROVIDER", "llm_provider"))
    model_name: str = Field(default="llama-3.3-70b-versatile", validation_alias=AliasChoices("MODEL_NAME", "model_name"))
    groq_api_key: Optional[str] = Field(default=None, validation_alias=AliasChoices("GROQ_API_KEY", "groq_api_key"))
    
    # OpenAI configurations (optional/legacy)
    openai_api_key: Optional[str] = Field(default=None, validation_alias=AliasChoices("OPENAI_API_KEY", "openai_api_key"))
    openai_embedding_model: Optional[str] = Field(default=None, validation_alias=AliasChoices("OPENAI_EMBEDDING_MODEL", "openai_embedding_model"))
    openai_embedding_dimensions: Optional[int] = Field(default=None, validation_alias=AliasChoices("OPENAI_EMBEDDING_DIMENSIONS", "openai_embedding_dimensions"))
    
    # Local Embeddings settings
    embedding_model: str = Field(default="BAAI/bge-small-en-v1.5", validation_alias=AliasChoices("EMBEDDING_MODEL", "embedding_model"))
    embedding_dimensions: int = Field(default=384, validation_alias=AliasChoices("EMBEDDING_DIMENSIONS", "embedding_dimensions"))
    
    # CORS Origins
    allowed_origins: str = Field(default="http://localhost:3000", validation_alias=AliasChoices("ALLOWED_ORIGINS", "allowed_origins"))

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
