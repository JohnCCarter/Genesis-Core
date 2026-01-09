from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

from core.symbols.symbols import SymbolMode


class Settings(BaseSettings):
    """
    Settings for the application.
    Reads from .env file and environment variables.
    """

    # Bitfinex API
    BITFINEX_API_KEY: str | None = None
    BITFINEX_API_SECRET: str | None = None
    BITFINEX_WS_API_KEY: str | None = None
    BITFINEX_WS_API_SECRET: str | None = None
    # Keep raw env as string to avoid ValidationError when empty
    SYMBOL_MODE: str = "realistic"
    LOG_LEVEL: str = "INFO"
    BEARER_TOKEN: str | None = None
    WALLET_CAP_ENABLED: int = 0

    @property
    def symbol_mode(self) -> SymbolMode:
        try:
            return SymbolMode(str(self.SYMBOL_MODE or SymbolMode.REALISTIC))
        except Exception:
            return SymbolMode.REALISTIC

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


def get_settings() -> Settings:
    return Settings()
