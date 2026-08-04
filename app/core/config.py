from typing import List, Optional
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings using Pydantic Settings."""

    # App Environment
    APP_NAME: str = "Telegram Services Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Telegram Bot
    BOT_TOKEN: SecretStr
    # Defined as str/raw input first to prevent pydantic-settings from pre-parsing as JSON
    REQUIRED_CHANNELS: str = ""
    REQUIRED_CHANNEL_IDS: str = ""

    # PostgreSQL Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5434
    POSTGRES_DB: str = "telegram_platform_db"
    
    # Redis
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # API Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def required_channels_list(self) -> List[str]:
        """Convert comma-separated REQUIRED_CHANNELS string into a clean list of channel usernames."""
        val = self.REQUIRED_CHANNELS.strip()
        if not val:
            return []
        # Support both comma-separated string and JSON array string
        if val.startswith("[") and val.endswith("]"):
            import json
            try:
                parsed = json.loads(val)
                if isinstance(parsed, list):
                    return [str(ch).strip() for ch in parsed if str(ch).strip()]
            except json.JSONDecodeError:
                pass
        return [ch.strip() for ch in val.split(",") if ch.strip()]

    @property
    def required_channel_ids_list(self) -> List[int]:
        """Convert comma-separated REQUIRED_CHANNEL_IDS string into a clean list of integer IDs."""
        val = str(self.REQUIRED_CHANNEL_IDS).strip()
        if not val:
            return []
        if val.startswith("[") and val.endswith("]"):
            import json
            try:
                parsed = json.loads(val)
                if isinstance(parsed, list):
                    return [int(cid) for cid in parsed]
            except (json.JSONDecodeError, ValueError):
                pass
        
        result = []
        for cid in val.split(","):
            cid_str = cid.strip()
            if cid_str:
                result.append(int(cid_str))
        return result

    @property
    def database_url(self) -> str:
        """Construct Async PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


# Singleton instance of Settings
settings = Settings()