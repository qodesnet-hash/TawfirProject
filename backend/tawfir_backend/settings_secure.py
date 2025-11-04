import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# ══════════════════════════════════════════════════════════════════
# SECURITY SETTINGS - ⚠️ CRITICAL
# ══════════════════════════════════════════════════════════════════

# إنشاء مفتاح سري قوي:
# python -c "import secrets; print(secrets.token_urlsafe(50))"
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("⚠️ SECRET_KEY must be set in .env file!")

# وضع التطوير/الإنتاج
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# المضيفون المسموح بهم (مهم جداً للأمان!)
ALLOWED_HOSTS_STR = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',')]

# ══════════════════════════════════════════════════════════════════
# HTTPS & SECURITY HEADERS
# ══════════════════════════════════════════════════════════════════

if not DEBUG:
    # إجبار HTTPS في الإنتاج
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # سنة واحدة
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
else:
    # إعدادات التطوير
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ══════════════════════════════════════════════════════════════════
# CORS SETTINGS - محددة وآمنة
# ══════════════════════════════════════════════════════════════════

CORS_ALLOW_ALL_ORIGINS = False  # ✅ تم إصلاحها
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS_STR = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:8100')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ALLOWED_ORIGINS_STR.split(',')]

# إضافة ngrok للتطوير فقط
if DEBUG:
    ngrok_url = os.getenv('NGROK_URL', '')
    if ngrok_url:
        CORS_ALLOWED_ORIGINS.append(ngrok_url)
        ALLOWED_HOSTS.append(ngrok_url.replace('https://', '').replace('http://', ''))
    
    # Capacitor/Ionic
    CORS_ALLOWED_ORIGINS.extend([
        'capacitor://localhost',
        'ionic://localhost',
        'http://localhost',
    ])

CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# إضافة header لـ ngrok فقط في التطوير
if DEBUG:
    CORS_ALLOW_HEADERS.append('ngrok-skip-browser-warning')

CORS_EXPOSE_HEADERS = ['Content-Type', 'Content-Disposition']

CSRF_TRUSTED_ORIGINS_STR = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if CSRF_TRUSTED_ORIGINS_STR:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_STR.split(',')]
else:
    CSRF_TRUSTED_ORIGINS = []

# ══════════════════════════════════════════════════════════════════
# APPLICATIONS
# ══════════════════════════════════════════════════════════════════

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Security
    'axes',  # حماية من Brute Force
    'csp',   # Content Security Policy
    
    # Third party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    
    # Local apps
    'api',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Security middleware
    'csp.middleware.CSPMiddleware',
    'axes.middleware.AxesMiddleware',  # Brute force protection
]

ROOT_URLCONF = 'tawfir_backend.urls'

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

WSGI_APPLICATION = 'tawfir_backend.wsgi.application'

# ══════════════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════════════

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# ══════════════════════════════════════════════════════════════════
# PASSWORD VALIDATION
# ══════════════════════════════════════════════════════════════════

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ══════════════════════════════════════════════════════════════════
# INTERNATIONALIZATION
# ══════════════════════════════════════════════════════════════════

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_TZ = True

# ══════════════════════════════════════════════════════════════════
# STATIC & MEDIA FILES
# ══════════════════════════════════════════════════════════════════

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / os.getenv('MEDIA_ROOT', 'media')

# حد أقصى لحجم الملفات (5MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.CustomUser'

# ══════════════════════════════════════════════════════════════════
# THIRD PARTY SERVICES
# ══════════════════════════════════════════════════════════════════

# Twilio
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

# ══════════════════════════════════════════════════════════════════
# REST FRAMEWORK
# ══════════════════════════════════════════════════════════════════

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    
    # ✅ Rate Limiting محسّن
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',          # ✅ تم تقليله من 1000
        'user': '1000/hour',         # ✅ تم تقليله من 10000
        'auth': '10/minute',         # للتسجيل والدخول
        'review': '5/hour',          # للمراجعات
        'upload': '10/hour',         # لرفع الصور
    },
    
    # إعدادات إضافية للأمان
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# إضافة BrowsableAPI فقط في التطوير
if DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
        'rest_framework.renderers.BrowsableAPIRenderer'
    )

# ══════════════════════════════════════════════════════════════════
# JWT SETTINGS - ✅ محسّن
# ══════════════════════════════════════════════════════════════════

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),      # ✅ تم تقليله من 7 أيام
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),      # ✅ تم تقليله من 30 يوم
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    
    # إعدادات أمان إضافية
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# ══════════════════════════════════════════════════════════════════
# DJANGO-AXES (Brute Force Protection)
# ══════════════════════════════════════════════════════════════════

AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5  # عدد المحاولات الفاشلة
AXES_COOLOFF_TIME = 1   # ساعة واحدة ban
AXES_LOCK_OUT_AT_FAILURE = True
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = None
AXES_LOCKOUT_URL = None
AXES_VERBOSE = True
AXES_ONLY_USER_FAILURES = False  # حماية بالـ IP أيضاً

# استخدام IP الحقيقي خلف Proxy
AXES_META_PRECEDENCE_ORDER = [
    'HTTP_X_FORWARDED_FOR',
    'REMOTE_ADDR',
]

# ══════════════════════════════════════════════════════════════════
# CONTENT SECURITY POLICY
# ══════════════════════════════════════════════════════════════════

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")  # للـ inline scripts
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "data:")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)  # منع embedding

# ══════════════════════════════════════════════════════════════════
# LOGGING - محسّن
# ══════════════════════════════════════════════════════════════════

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
            'filters': ['require_debug_false'],
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'axes': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# إنشاء مجلد logs إذا لم يكن موجود
import os
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ══════════════════════════════════════════════════════════════════
# ADMINS - للتنبيهات
# ══════════════════════════════════════════════════════════════════

ADMINS = [
    ('Admin', os.getenv('ADMIN_EMAIL', 'admin@tawfir.app')),
]

MANAGERS = ADMINS

# ══════════════════════════════════════════════════════════════════
# SESSION SECURITY
# ══════════════════════════════════════════════════════════════════

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # يوم واحد
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# ══════════════════════════════════════════════════════════════════
# استيراد إعدادات إضافية خاصة بالبيئة
# ══════════════════════════════════════════════════════════════════

# للإنتاج: settings_production.py
# للتطوير: settings_development.py

print(f"✅ Settings loaded - Environment: {'Production' if not DEBUG else 'Development'}")
