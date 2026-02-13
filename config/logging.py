# config/logging.py
"""
Global production-ready logging setup for entire project.
Import in settings.py: from config.logging import LOGGING
Works for all apps (auth_app, admin, recruiter, future apps)
"""

import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

BASE_DIR = Path(__file__).resolve().parent.parent  

# Create logs folder automatically
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s | %(levelname)8s | %(name)30s | %(message)s | %(filename)s:%(lineno)d',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'app.log'),
            'maxBytes': 10 * 1024 * 1024,  
            'backupCount': 7,              
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'errors.log'),
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        '': {  
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),  
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'error_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}