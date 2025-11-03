"""Backend package initialization."""
from .main import app
from .config import get_settings
from .opensearch_client import get_opensearch_client

__all__ = ["app", "get_settings", "get_opensearch_client"]
