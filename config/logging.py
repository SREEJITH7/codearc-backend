# import os 
# from pathlib import Path
# from logging.handlers import RotatingFileHandler


# BASE_DIR = Path(__file__).resolve().parent.parent

# LOGS_DIR = os.path.join(BASE_DIR,'logs')
# os.makedirs(LOGS_DIR, exist_ok=True)

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{asctime} | {levelname:8} | {name:25} | {message} | {filename}:{lineno}',
#             'style': '{',
#             'datefmt': '%Y-%m-%d %H:%M:%S',
#         },
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'verbose',
#         },
#         'file': {
#             'level': 'INFO',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': os.path.join(LOGS_DIR, 'app.log'),
#             'maxBytes': 10 * 1024 * 1024,  # 10MB per file
#             'backupCount': 5,  # Keep 5 backups
#             'formatter': 'verbose',
#             'encoding': 'utf-8',
#         },
#         'error_file': {
#             'level': 'ERROR',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': os.path.join(LOGS_DIR, 'errors.log'),
#             'maxBytes': 10 * 1024 * 1024,
#             'backupCount': 5,
#             'formatter': 'verbose',
#             'encoding': 'utf-8',
#         },
#     },
#     'loggers': {
#         '': {  # Root logger
#             'handlers': ['console', 'file'],
#             'level': 'INFO',
#             'propagate': True,
#         },
#         'auth_app': {  # Your app name
#             'handlers': ['console', 'file', 'error_file'],
#             'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),  # Env var for dev/prod switch
#             'propagate': False,
#         },
#         'django': {
#             'handlers': ['console'],
#             'level': 'INFO',
#             'propagate': False,
#         },
#     },
# }



