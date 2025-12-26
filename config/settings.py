  
from pathlib import Path
import os
from dotenv import load_dotenv
# from config.logging import LOGGING


# LOGGING = LOGGING

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")





# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-*761tkjr1*u446utbrzc1agu+h)6q!#jwpywz%^5w474rsy08'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# IMPORTANT: include hosts you use in dev
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',  # MUST be before Django apps/middleware
    'rest_framework',

    # Local apps
    
    'apps.auth_app',
    "apps.user_app",
    "apps.recruiter_app",

]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # MUST be at top
    # "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "common.middleware.jwt_cookie_middleware.JwtCookieToHeaderMiddleware",  # your custom middleware
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database (unchanged)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Password validation (unchanged)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'auth_app.User'

# Email (console for dev)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

# ============================================================================
# CORS CONFIGURATION (for frontend on localhost:5173)
# ============================================================================
# When using credentials, CORS_ALLOW_CREDENTIALS must be True and you must NOT
# use wildcard origins.
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_EXPOSE_HEADERS = [
    "Content-Type",
    "X-CSRFToken",
]

CORS_PREFLIGHT_MAX_AGE = 86400

# ============================================================================
# COOKIE / CSRF / SESSION CONFIGURATION
# ============================================================================

# Add the exact origins as trusted origins for CSRF.
# NOTE: include the scheme (http/https).
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",    # 🔥 ADD THIS
    "http://127.0.0.1:5174",    # 🔥 ADD THIS
]

# === IMPORTANT SECURITY / cross-site cookie settings ===
# For cross-site cookies (frontend at different origin) browsers require:
#    SameSite=None AND Secure=True
#
# In production you MUST use HTTPS so Secure=True is appropriate.
# For local dev you can use mkcert/ngrok or enable HTTPS on the dev server.
#
# If you cannot use HTTPS during development, see the note at the end of this file.

# CSRF cookie
# CSRF_COOKIE_SECURE = True            # requires HTTPS in browsers
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False         # keep False if frontend reads CSRF token
# CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SAMESITE = "Lax" 
CORS_ALLOW_CREDENTIALS = True
# Session cookie
# SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = False        # Must be False for HTTP localhost

SESSION_COOKIE_HTTPONLY = True
# SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SAMESITE = "Lax"

# JWT cookie names used by your app
ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"

# Custom cookie config for JWT cookies
# COOKIE_SECURE = True
# COOKIE_SAMESITE = "None"

# Custom cookie config for JWT cookies (used in your views)
COOKIE_SECURE = False                # Must be False for HTTP localhost
COOKIE_SAMESITE = "Lax"              # "Lax" works for localhost
COOKIE_HTTPONLY = True

# Ensure cookie domain/path are set so browser sends cookies for API routes
COOKIE_PATH = "/"
COOKIE_DOMAIN = None  # None lets browser use the current host (localhost / 127.0.0.1)

# If you need to expose cookies to JS (not recommended for JWT access token),
# set COOKIE_HTTPONLY = False — but keep refresh cookie HttpOnly for safety.

# ============================================================================
# Optional: Other settings you already had
# ============================================================================
CSRF_COOKIE_DOMAIN = None
SESSION_COOKIE_DOMAIN = None


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# ...

# ===============================
# 🔥 FIX POPUP GOOGLE LOGIN BUG
# ===============================
X_FRAME_OPTIONS = "ALLOWALL"  
# Prevents Django from blocking popup callback page

SECURE_CROSS_ORIGIN_OPENER_POLICY = None  
SECURE_CROSS_ORIGIN_EMBEDDER_POLICY = None  
# Allows popup → opener communication (postMessage)

SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"
# Helps prevent Google redirect being blocked

GITHUB_REDIRECT_URI = "http://localhost:8000/api/auth/github/callback/"


CACHES = {
    "default": {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION' : 'redis://127.0.0.1:6379/1', 
        'OPTIONS':{
            'CLIENT_CLASS' : 'django_redis.client.DefaultClient',
        }
    }
}


# Use Redis for sessions too
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"



# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# DEFAULT_FROM_EMAIL = "CodeArc <noreply@codearc.local>"


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = "karnjaps4@gmail.com"
EMAIL_HOST_PASSWORD = "tkgqmezdpsoiahxl"

DEFAULT_FROM_EMAIL = "CodeArc <yourgmail@gmail.com>"



    