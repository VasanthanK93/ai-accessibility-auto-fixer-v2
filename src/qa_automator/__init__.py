"""QA Automator package."""

from .analyzer import QAAnalyzer
from .backends import MockBackend, OllamaBackend

__all__ = ["QAAnalyzer", "MockBackend", "OllamaBackend"]
