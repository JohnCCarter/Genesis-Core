"""
Trial result caching to avoid re-running identical trials.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class TrialResultCache:
    """
    Cache for trial results to avoid re-running identical parameter combinations.
    
    Uses filesystem-based caching with content-addressable storage based on
    parameter fingerprints.
    """
    
    def __init__(self, cache_dir: Path) -> None:
        """
        Initialize trial result cache.
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def lookup(self, fingerprint: str) -> dict[str, Any] | None:
        """
        Look up cached result by parameter fingerprint.
        
        Args:
            fingerprint: Unique fingerprint of trial parameters
            
        Returns:
            Cached trial result dict if found, None otherwise
        """
        cache_file = self.cache_dir / f"{fingerprint}.json"
        if not cache_file.exists():
            return None
        
        try:
            content = cache_file.read_text(encoding="utf-8")
            return json.loads(content)
        except (OSError, json.JSONDecodeError):
            # Cache file corrupted or unreadable, treat as cache miss
            return None
    
    def store(self, fingerprint: str, result: dict[str, Any]) -> None:
        """
        Store trial result in cache.
        
        Args:
            fingerprint: Unique fingerprint of trial parameters
            result: Trial result dict to cache
        """
        cache_file = self.cache_dir / f"{fingerprint}.json"
        
        try:
            # Use atomic write to avoid partial writes
            import tempfile
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                delete=False,
                dir=self.cache_dir
            ) as tmp:
                json.dump(result, tmp, indent=2)
                tmp_path = tmp.name
            
            Path(tmp_path).replace(cache_file)
        except OSError:
            # Silently ignore cache write failures
            pass
    
    def clear(self) -> int:
        """
        Clear all cached results.
        
        Returns:
            Number of cache files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except OSError:
                pass
        return count


__all__ = ["TrialResultCache"]
