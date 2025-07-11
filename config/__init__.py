"""Configuration module for Scientific Paper Analyzer"""

from .database_config import get_database_config, get_database_url, DEFAULT_CONFIG

__all__ = ['get_database_config', 'get_database_url', 'DEFAULT_CONFIG']