"""
Core functionality for RevBot.
"""
from .claude_client import ClaudeClient
from .logging import get_logger

__all__ = ["ClaudeClient", "get_logger"]