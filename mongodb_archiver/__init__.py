"""
MongoDB Order Archiver
Professional order archiving system with Change Streams support
"""

__version__ = '2.0.0'
__author__ = 'MongoDB Archiver Team'

from .config import Config
from .archiver import OrderArchiver
from .watcher import OrderWatcher
from .generator import DataGenerator

__all__ = [
    'Config',
    'OrderArchiver',
    'OrderWatcher',
    'DataGenerator'
]
