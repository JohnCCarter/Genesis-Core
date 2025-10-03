from __future__ import annotations

from pydantic_settings import BaseSettings

from core.symbols.symbols import SymbolMode

class Settings(BaseSettings):
    BITFINEX_API_KEY: str | None = None
    BITFINEX_API_SECRET: str | None = None
    BITFINEX_WS_API_KEY: str | None = None
    BITFINEX_WS_API_SECRET: str | None = None
    SYMBOL_MODE: SymbolMode = SymbolMode.REALISTIC

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    return Settings()
