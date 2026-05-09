"""
Django settings for NameProject project.
Optimized for production performance.
"""

from pathlib import Path
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==================== БЕЗОПАСНОСТЬ ====================
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())


# ==================== ПРИЛОЖЕНИЯ ====================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Сторонние приложения
    'django_telegram_login',
    'corsheaders',
    'captcha',
    
    # Собственные приложения
    'main',
    'users',
    'orders',
    'reviews',
    'about',
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
]

ROOT_URLCONF = 'NameProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins': ['django.templatetags.static'],
        },
    },
]

WSGI_APPLICATION = 'NameProject.wsgi.application'


# ==================== БАЗА ДАННЫХ ====================
if config('DB_ENGINE', default='sqlite') == 'django.db.backends.mysql':
    DATABASES = {
        'default': {
            'ENGINE': config('DB_ENGINE'),
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT', default='3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            },
            'CONN_MAX_AGE': 60,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / config('DB_NAME', default='db.sqlite3'),
            'OPTIONS': {
                'timeout': 20,
            }
        }
    }


# ==================== ПРОВЕРКА ПАРОЛЕЙ ====================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==================== ИНТЕРНАЦИОНАЛИЗАЦИЯ ====================
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Krasnoyarsk'
USE_I18N = True
USE_TZ = True


# ==================== СТАТИЧЕСКИЕ ФАЙЛЫ ====================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Сжатие статики при collectstatic
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/'


# ==================== КЭШИРОВАНИЕ ====================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Кэширование шаблонов (включить в продакшене)
if not DEBUG:
    TEMPLATES[0]['APP_DIRS'] = False
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]


# ==================== АУТЕНТИФИКАЦИЯ ====================
AUTH_USER_MODEL = 'users.User'
LOGIN_URL = '/user/login/'
LOGIN_REDIRECT_URL = 'main:index'
LOGOUT_REDIRECT_URL = 'main:index'


# ==================== TELEGRAM ====================
TELEGRAM_BOT_NAME = config('TELEGRAM_BOT_NAME', default='')
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='')
TELEGRAM_LOGIN_REDIRECT_URL = config('TELEGRAM_LOGIN_REDIRECT_URL', default='')
TELEGRAM_LOGIN_CALLBACK_URL = config('TELEGRAM_LOGIN_CALLBACK_URL', default='users:telegram_login')

# Telegram уведомления
TELEGRAM_NOTIFICATION_BOT_TOKEN = config('TELEGRAM_NOTIFICATION_BOT_TOKEN', default='')
TELEGRAM_CHAT_ID = config('TELEGRAM_CHAT_ID', default='')

# SITE_URL для Telegram уведомлений
SITE_URL = config('SITE_URL', default='https://hair-braider.ru')


# ==================== БЕЗОПАСНОСТЬ ====================
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='https://hair-braider.ru/', cast=Csv())
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='https://hair-braider.ru/,http://localhost:8000', cast=Csv())

# Настройки сессий - только для продакшена
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
else:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

SESSION_COOKIE_AGE = 86400  # 24 часа
SESSION_SAVE_EVERY_REQUEST = True


# ==================== API КЛЮЧИ ====================
GOOGLE_RECAPTCHA_SECRET_KEY = config('GOOGLE_RECAPTCHA_SECRET_KEY', default='')
SMSRU_API_ID = config('SMSRU_API_ID', default='')


# ==================== ФОРМАТЫ ДАТ ====================
DATE_INPUT_FORMATS = ['%d.%m.%Y', '%Y-%m-%d']
TIME_INPUT_FORMATS = ['%H:%M', '%I:%M %p']


# ==================== НАСТРОЙКИ ДЛЯ PRODUCTION ====================
if not DEBUG:
    # HTTPS настройки - ОТКЛЮЧЕНЫ для Timeweb (Nginx уже обрабатывает HTTPS)
    # SECURE_SSL_REDIRECT = True
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True
    
    # Дополнительные заголовки безопасности
    X_FRAME_OPTIONS = 'DENY'
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True


# ==================== LOGGING ====================
# Создание директории для логов
LOG_DIR = BASE_DIR / 'logs'
if not LOG_DIR.exists():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR' if not DEBUG else 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'debug.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


# ==================== DEFAULT PRIMARY KEY ====================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==================== ПЕРЕМЕННЫЕ ДЛЯ TELEGRAM СЕРВИСА ====================
# Для совместимости с телеграм сервисом
TELEGRAM_BOT_TOKEN_FOR_NOTIFIER = TELEGRAM_NOTIFICATION_BOT_TOKEN