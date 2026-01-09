"""Cryptographic utilities for Genesis-Core."""

import hashlib
import hmac


def build_hmac_signature(secret: str, message: str) -> str:
    """
    Build HMAC-SHA384 signature for Bitfinex API authentication.

    Args:
        secret: API secret key
        message: Message to sign

    Returns:
        Hexadecimal signature string
    """
    return hmac.new(secret.encode(), message.encode(), hashlib.sha384).hexdigest()
