from .config import Settings as _Settings

settings = _Settings()
Settings = _Settings

__all__ = ("settings", "Settings")