import os.path
import sys
from datetime import timedelta
from email.policy import default
from pathlib import Path
from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.join(BASE_DIR,'apps'))
SECRET_KEY = config('SECRET_KEY',default="hjg^&%**%%^*GHVGJHGKJGKH")

STRIPE_TEST_PUBLIC_KEY = config('STRIPE_TEST_PUBLIC_KEY')
STRIPE_TEST_SECRET_KEY = config('STRIPE_TEST_SECRET_KEY')

DEBUG = config('DEBUG',default=False,cast=bool)
AUTH_USER_MODEL = 'user.User'

ALLOWED_HOSTS = []

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

EXTERNAL_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'django_filters',
]

LOCAL_APPS = [
    'user',
    'share',
    'product',
    'cart',
    'order',
    'payment'
]

INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Database

DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE",default="django.db.backends.sqlite3"),
        "NAME": config("DB_NAME",default=BASE_DIR / "db.sqlite3"),
        "USER":config("DB_USER",default=''),
        "PASSWORD":config("DB_PASSWORD",default=''),
        "HOST":config("DB_HOST",default=''),
        "PORT":config("DB_PORT",default='')
    }
}

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Tashkent"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# redis setup
REDIS_HOST = config("REDIS_HOST",default="localhost")
REDIS_PORT = config("REDIS_PORT",default="6379")
REDIS_DB = config("REDIS_DB",default='1')

REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

CACHES = {
    'default':{
        'BACKEND':'django_redis.cache.RedisCache',
        'LOCATION':REDIS_URL,
        'OPTIONS':{
            'CLIENT_CLASS':'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# celery setup
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TIMEZONE='Asia/Tashkent'
# stripe setup


# rest_framework setup
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES':[
        # 'rest_framework.authentication.BasicAuthentication',
        'user.authentications.CustomJWTAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS':'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE':10
}

AUTHENTICATION_BACKENDS = [
     'user.backends.CustomModelBackend'
]

SPECTACULAR_SETTINGS = {
    'TITLE': 'Alibaba Clone backend',
    'DESCRIPTION': 'This is backend Api for Ecommerce',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST':True
    # OTHER SETTINGS
}

# email
EMAIL_BACKEND = config('EMAIL_BACKEND', default='')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default='')
EMAIL_PORT = config('EMAIL_PORT', default='')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')


# jwt setup
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=10),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JSON_ENCODER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=60),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=10),
}


# logging setup
