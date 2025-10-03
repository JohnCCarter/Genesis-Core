from __future__ import annotations

from pydantic_settings import BaseSettings

from core.symbols.symbols import SymbolMode


class Settings(BaseSettings):
    BITFINEX_API_KEY: str | None = None
    BITFINEX_API_SECRET: str | None = None
    BITFINEX_WS_API_KEY: str | None = None
    BITFINEX_WS_API_SECRET: str | None = None
    # Keep raw env as string to avoid ValidationError when empty
    SYMBOL_MODE: str = "realistic"
    BEARER_TOKEN: str | None = None
    WALLET_CAP_ENABLED: int = 0

    @property
    def symbol_mode(self) -> SymbolMode:
        try:
            return SymbolMode(str(self.SYMBOL_MODE or SymbolMode.REALISTIC))
        except Exception:
            return SymbolMode.REALISTIC

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    return Settings()
